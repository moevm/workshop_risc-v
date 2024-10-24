#include <cstdint>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <cstring>
#include <string>

#include <signal.h>
#include <stdint.h>

#ifndef MAX_N_ENTRIES
#define MAX_N_ENTRIES 32
#endif

#ifndef A_TYPE
#define A_TYPE int64_t
#endif

#ifndef B_TYPE
#define B_TYPE int64_t
#endif

#ifndef C_TYPE
#define C_TYPE int64_t
#endif

#ifndef RESULT_TYPE
#define RESULT_TYPE int64_t
#endif

#pragma pack(push, 1)
struct entry_t {
    RESULT_TYPE (*function_ptr)();
    int16_t cnt;
};

struct table_t {
    int8_t unused[6];
    int32_t n;

    entry_t data[MAX_N_ENTRIES];
};
#pragma pack(pop)

static_assert(sizeof(table_t) == 10*(MAX_N_ENTRIES + 1), "Wrong sizeof(table_t)");

enum location_t {
    STUDWORK_CODE,
    CHECKER_CODE
};

// global symbols
A_TYPE a;
B_TYPE b;
C_TYPE c;
table_t listener_table;

// local symbols
static table_t *table_copy; // store it somewhere else in memory
                            // so student can`t access it accidentally
static int n_entries, n_calls;
static location_t location = CHECKER_CODE;
static size_t stud_entry_index;
static const char *err_msg;

// external functions
extern "C" void load();
extern "C" void unload();

RESULT_TYPE basic_handler()
{
    return 0;
}

void check_integrity()
{
    for (int i = 0; i < MAX_N_ENTRIES; i++) {
        if (i == stud_entry_index)
            continue;

        if (memcmp(&table_copy->data[i], &listener_table.data[i], sizeof(entry_t)) != 0)
            throw std::runtime_error("Ваша программа поменяла не ту строку в таблице");
    }
}

void signal_hander(int sig)
{
    std::cerr << err_msg << ": программа завершила работу с кодом " << sig << '\n';
    if (location == CHECKER_CODE) {
        std::cerr << "Скорее всего это внутренняя ошибка проверяющей системы\n";
    }
    exit(sig);
}

void setup_signal_handers()
{
    struct sigaction siga;
    siga.sa_handler = signal_hander;
    for (int sig = 1; sig <= SIGRTMAX; ++sig) {
        sigaction(sig, &siga, NULL);
    }
}

void init_table()
{
    std::cin >> n_entries >> n_calls;
    
    memset(&listener_table, 0x7F, sizeof(listener_table));
    listener_table.n = n_entries;

    for (int i = 0; i < n_entries; i++) {
        listener_table.data[i].cnt = rand();
        listener_table.data[i].function_ptr = basic_handler;
    }

    table_copy = (table_t*)malloc(sizeof(listener_table));
    memcpy(table_copy, &listener_table, sizeof(listener_table));

    stud_entry_index = n_entries;
}

void load_table()
{
    init_table();

    location = STUDWORK_CODE;
    load();
    location = CHECKER_CODE;

    check_integrity();

    if (listener_table.n != n_entries + 1)
        throw std::runtime_error("Ваша программа неправильно обновила заголовок таблицы (либо не обновила его вообще)");

    if (listener_table.data[stud_entry_index].cnt != 0)
        throw std::runtime_error("Ваша программа не установила значение счетчика равным нулю");

    if (listener_table.data[stud_entry_index].function_ptr == (void*)0x7F7F7F7F7F7F7F7Fu)
        throw std::runtime_error("Ваша программа не установила указатель на функцию-обработчик");
}

void run_tests()
{
    while (n_calls--) {
        entry_t &entry = listener_table.data[stud_entry_index];
        entry_t entry_old = entry;

        // std::cin interprets int8_t as characters, not numbers... so these things are uintmax_t...
        uintmax_t a_copy;
        uintmax_t b_copy;
        uintmax_t c_copy;
        uintmax_t expected;

        std::cin >> a_copy >> b_copy >> c_copy >> expected;
        
        a = a_copy;
        b = b_copy;
        c = c_copy;

        location = STUDWORK_CODE;
        RESULT_TYPE res = entry.function_ptr();
        location = CHECKER_CODE;

        if (res != expected) {
            throw std::runtime_error(
                "Неправильный ответ\n"
                "  Входные данные: "
                      "a = " + std::to_string((A_TYPE)a_copy) +
                    ", b = " + std::to_string((B_TYPE)b_copy) +
                    ", c = " + std::to_string((C_TYPE)c_copy) + "\n"
                "  Результат: a0 = " + std::to_string(res) + "\n"
                "  Ожидалось: a0 = " + std::to_string((RESULT_TYPE)expected)
            );
        }
        
        check_integrity();
        
        if (entry.cnt != entry_old.cnt + 1)
            throw std::runtime_error("Ваша программа неправильно обновила счетчик количества вызовов обработчика (либо не обновила его вообще)");

        if (entry.function_ptr != entry_old.function_ptr)
            throw std::runtime_error("Указатель на функцию в строке вашего обработчика был изменен");
    }
}

void unload_table()
{
    location = STUDWORK_CODE;
    unload();
    location = CHECKER_CODE;

    check_integrity();

    if (listener_table.n != n_entries)
        throw std::runtime_error("Ваша программа неправильно обновила заголовок таблицы");
}

int main()
{
    setup_signal_handers();

    try {
        err_msg = "Ошибка при вызове load()";
        load_table();

        err_msg = "Ошибка при вызове обработчика";
        run_tests();
        
        err_msg = "Ошибка при вызове unload()";
        unload_table();
    }
    catch (std::exception &e) {
        std::cerr << err_msg << ": " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
