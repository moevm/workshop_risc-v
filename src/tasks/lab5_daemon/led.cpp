//#include <exception>
#include <climits>
#include <mutex>
#include <iostream>
#include <string>
#include <sstream>
#include <thread>
#include <string.h> // for parsing argc/argv
#include <unistd.h> // for usleep
#include <csignal> // for SIGSEGV.....
#include <vector>

#define N_BUTTONS 8
#define N_LEDS 8

#ifndef TIME_MULTIPLIER
#define TIME_MULTIPLIER 3
#endif

#define THINK_TIME_US ((int)((TIME_MULTIPLIER) * 1000))
#define SLEEP_TIME_US 1000

typedef unsigned long long llu_t;

volatile static llu_t buttons;
volatile static llu_t leds;

static int is_interactive;
volatile static int sleep_cnt;
volatile static int is_child_still_running = 1;

std::stringstream ss;
std::mutex mutex;
static int n_messages;

struct _devnull : std::basic_ostream<char> {
    template<class T>
    _devnull &operator <<(T a) { return *this; }
} devnull;

struct logger {
    logger() {
        if (is_interactive) {
            std::cout << '\r';
        }
        mutex.lock();
    }

    std::basic_ostream<char> &get() { 
        if (is_child_still_running == 0)
            return devnull;

        std::basic_ostream<char> &res = (is_interactive ? std::cout : ss);
        res << "[" << n_messages++ << "] ";
        return res;
    }

    ~logger()
    {
        if (is_interactive) {
            std::cout << "> ";
        }
        mutex.unlock();
    }
};

std::string binary(llu_t val, int n)
{
    std::string res;

    res.push_back('[');
    bool need_comma = false;
    
    for (int i = 0; i < n; i++) {
        if (val & 1) {
            if (need_comma) {
                res += ", ";
            } else {
                need_comma = true;
            }
            res += std::to_string(i);
        }
        val >>= 1;
    }
    res.push_back(']');
    
    if (!need_comma) {
        res += " (список пуст)";
    }
    return res;
}

void fatal_error(const char *error_str) {
    std::cout <<
        "Ошибка: " << error_str << "\n"
        "(см. логи для большей информации)" << std::endl;
    
    if (!is_interactive) {
        std::cout << "\n -- ЛОГИ --\n"
            "ИНФО: Числа в квадратных скобках - это порядковые номера сообщений\n"
            "ИНФО: Меткой ТЕСТ помечены действия тестирующей системы.\n"
            "ИНФО: Меткой ПРОГ помечены действия, происходящие внутри вашей программы\n"
            << ss.rdbuf() << std::endl;
    }
    
    exit(1);
}

extern "C" int get_button_status(int button_number)
{
    if (button_number < 0 || button_number >= N_BUTTONS) {
        logger().get() <<
            "ПРОГ: get_button_status(" << button_number << ") ---> ???\n"
            "    ПРОГ: указан некорректный номер кнопки (номер кнопки должен быть в диапазоне от 0 до " << N_BUTTONS - 1 << " включительно)\n"
            "    ПРОГ: завершаем работу..." << std::endl; 
        fatal_error("неправильное использование get_button_status");
    }

    int ret = (buttons >> button_number) & 1;
    if (!is_interactive) {
        logger().get() << "ПРОГ: get_button_status(" << button_number << ") ---> " << ret << std::endl;
    }

    return ret;
}

extern "C" void set_led_status(int led_number, int led_status)
{
    if (!is_interactive) {
        logger().get() << "ПРОГ: set_led_status(" << led_number << ", " << led_status << ")" << std::endl;
    }

    if (led_number < 0 || led_number >= N_LEDS) {
        logger().get() <<
            "ПРОГ: указан некорректный номер диода (номер диода должен быть в диапазоне от 0 до " << N_LEDS - 1 << " включительно)\n"
            "    ПРОГ: завершаем работу..." << std::endl;
        fatal_error("неправильное использование set_led_status");
    }
    
    llu_t new_leds = leds & (~(1 << led_number)) | ((led_status ? 1 : 0) << led_number);
    if (new_leds != leds) {
        logger().get() << "ПРОГ: set_led_status изменила список активных диодов: " << binary(new_leds, N_LEDS) << std::endl;
        leds = new_leds;
    }
}

extern "C" void delay()
{
    if (!is_child_still_running) {
        exit(0);
    }

    if (!is_interactive) {
        logger().get() << "ПРОГ: delay()" << std::endl;
    }

    sleep_cnt++;
    usleep(SLEEP_TIME_US);
}

bool cmd_buttons()
{
    std::cout << "Список зажатых кнопок: " << binary(buttons, N_BUTTONS) << '\n';
    return true;
}

bool cmd_leds()
{
    std::cout << "Список активных диодов: " << binary(leds, N_LEDS) << std::endl;
    return true;
}

bool cmd_set(std::vector<std::string> &args)
{
    if (args.size() != 3) {
        std::cout << "Неправильное количество аргументов" << std::endl;
        return false;
    }
    int idx = strtol(args[1].c_str(), NULL, 0);
    if (idx < 0 || idx >= N_BUTTONS) {
        std::cout << "Номер кнопки должен быть числом в диапазоне от 0 до " << N_BUTTONS - 1 << std::endl;
        return false;
    }
    int state = strtol(args[2].c_str(), NULL, 0);
    if (state != 0 && state != 1) {
        std::cout << "Неправильно состояние кнопки. 0 - выкл, 1 - вкл" << std::endl;
        return false;
    }
    buttons = (buttons & ~(1 << idx)) | (state << idx);
    return true;
}

bool cmd_hex(std::vector<std::string> &args)
{
    if (args.size() != 2) {
        std::cout << "Неправильное количество аргументов" << std::endl;
        return false;
    }
    long res = strtol(args[1].c_str(), NULL, 16);

    if (res < 0 || res >= (1 << N_BUTTONS)) {
        std::cout << "Аргумент должен быть числом в шестнадцатеричной записи в диапазоне от 0 до " 
                  << std::hex << (1 << N_BUTTONS) - 1 << std::dec << std::endl;
        return false;
    }

    buttons = res;
    return true;
}

void io_loop_interactive()
{
    static const char greet_msg[] =
        "Добро пожаловать в интерактивный режим\n"
        "Числа в квадратных скобках - это порядковые номера сообщений";

    static const char help_msg[] = 
        "Список доступных команд:\n"
        "  quit        - закончить работу программы\n"
        "  buttons     - вывести список зажатых кнопок\n"
        "  leds        - вывести список активных диодов\n"
        "  set X {0/1} - установить состояние кнопки с номером X (0 - выкл, 1 - вкл)\n"
        "  hex NUMBER  - установить битовую маску для кнопок (i-й бит отвечает за состояние i-й кнопки)\n"
        "                число NUMBER задается в шестнадцатеричном формате";

    std::cout << greet_msg << '\n' << help_msg << std::endl;

    while (1) {
        std::string line;
        std::cout << "\n> ";
        std::getline(std::cin, line);
    
        std::stringstream ss(line);  
        std::string word;
        std::vector<std::string> args;
        while (ss >> word) {
            args.push_back(word);
        }

        if (args.size() == 0)
            continue;

        {
            logger l; // lock logging;
            bool ok = false;

            if (args[0][0] == 'b')
                ok = cmd_buttons();
            else if (args[0][0] == 'l')
                ok = cmd_leds();
            else if (args[0][0] == 's')
                ok = cmd_set(args);
            else if (args[0][0] == 'h')
                ok = cmd_hex(args);
            else if (args[0][0] == 'q') {
                is_child_still_running = 0;
                std::cout << "Завершаем работу..." << std::endl;
                return;
            }
            
            if (!ok) {
                std::cout << help_msg << std::endl;
            }
        }
    }
}

void io_loop_testing()
{
    int n_states;
    std::cin >> n_states;

    while (n_states--) {
        llu_t new_buttons;
        llu_t expected_leds;
        std::cin >> new_buttons >> expected_leds;

        {
            logger().get() <<
                "ТЕСТ: состояние кнопок изменилось\n"
                "    ТЕСТ: список зажатых кнопок: " << binary(new_buttons, N_BUTTONS) << "\n"
                "    ТЕСТ: вашей программе дано " << THINK_TIME_US/1000 << " мс на ответ..." << std::endl;
            buttons = new_buttons;
        }

        usleep(THINK_TIME_US);

        if (is_child_still_running == 0) {
            logger().get() << "ТЕСТ: проверяемая программа завешила работу. завершаем тестирование..." << std::endl;
            throw std::runtime_error("проверяемая программа завешила работу");
        }

        if (leds != expected_leds) {
            logger().get()
                << "ТЕСТ: ваша программа установила неправильное состояние диодов\n" 
                   "    ТЕСТ: завершаем тестирование..." << std::endl;

            throw std::runtime_error(
                "неправильный ответ:\n"
                "  входные данные (список зажатых кнопок): " + binary(buttons, N_BUTTONS) + "\n"
                "  получено (список активных диодов):      " + binary(leds, N_LEDS) + "\n"
                "  ожидалось (список активных диодов):     " + binary(expected_leds, N_LEDS)
            );
        } else {
            logger().get() << "ТЕСТ: всё правильно, продолжаем тестирование..." << std::endl;
        }
    }

    if (sleep_cnt == 0) {
        is_child_still_running = 0;
        throw std::runtime_error("ваша программа не вызывала функцию delay()");
    }
}


const char *sig2str(int sig)
{
    switch (sig) {
    case SIGSEGV:
        return "SIGSEGV (попытка чтения или записи в чужую память)\n  обратите внимание на инструкции load и store, только они отвечают за работу с памятью";
    case SIGFPE:
        return "SIGFPE (попытка выполнения ошибочной арифметической операции)\n  например: деление на ноль";
    default:
        return "подробнее ознакомиться с сигналами в Linux можно [здесь]\n  (https://www.ic.unicamp.br/~celio/mc514/linux/linux_pgsignals.html)";
    }
}


void f(int sig) {
    logger().get() << "ПРОГ: сигнал " << sig << ", завершаем работу..." << std::endl;
    fatal_error(("ваша программа завершила работу с сигналом " + std::to_string(sig) + ": " + sig2str(sig)).c_str());
}

extern "C" void solution();
void thread_fn()
{
    static struct sigaction siga;
    siga.sa_handler = f;
    sigaction(SIGSEGV, &siga, NULL);
    sigaction(SIGFPE, &siga, NULL);

    solution();

    {
        logger().get() << "ПРОГ: программа неожиданно завершила работу (с помощью инструкции ret)" << std::endl;
        fatal_error("программа неожиданно завершила работу (с помощью инструкции ret)");
    }
}

const char usage_str[] = "usage: ./led [interactive]";

int main(int argc, char **argv)
{
    argc--; argv++;
    if (argc == 1) {
        if (strcmp(argv[0], "interactive") == 0)
            is_interactive = 1;
        else {
            fputs(usage_str, stderr);
            return 1;
        }
    }
    else if (argc > 1) {
        fputs(usage_str, stderr);
        return 1;
    }

    std::thread thread(thread_fn);
    try {
        (is_interactive ? io_loop_interactive() : io_loop_testing());
    } catch (std::exception &e) {
        fatal_error(e.what());
    }
    
    is_child_still_running = 0;
    thread.join();
}
