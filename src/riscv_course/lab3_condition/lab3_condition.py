from typing import Optional
import random
import time
import numpy as np
from riscv_course.base_module import BaseTaskClass, TestItem
import riscv_course.random_expressions.random_condition_loop as cond_generator


DEFAULT_MAX_LENGTH_DEVIATION = 5
ARRAY_DEFAULT_LEN = 10
CONDITION_DEFAULT_LEN = 3
TASK_DESCRIPTION = """
Требуется написать программу, которая использует разные режимы адресации для вычислений по массиву данных в памяти. Результатом выполнения вашей программы будет измененный массив в памяти.

В качестве исходных данных дается стартовый адрес в памяти для хранения массива, количество элементов в массиве и формула для требуемых вычислений (Вычисления включают изменения каждого элемента массива в зависимости от условия). Порядок операций в формуле соответствует порядку операций в языке Си. 

При автоматической проверке вашей программы исходные данные располагаются в регистрах следующим образом:
  - a1 - адрес памяти, где расположен массив
  - a2 - количество элементов в массиве
Считайте, что массив уже инициализирован и заполнен данными. Размер каждого элемента массива - 8 байт (dword).

Ваша программа должна иметь следующую структуру:

```
.globl solution
solution: 
    # при старте данной метки ваша программа должна выполнить 
    # необходимые вычисления и изменить элементы массива согласно ветке условия и формуле в ней
    ret 
```

Доступ к массиву (чтение, изменение) должен выполняться из памяти.

Формула для вычислений будет выведена ниже (arr[i] - элемент массива, считаем что arr[-1] == 0):
{expression}
"""
MAIN_S = r"""
.globl main
.text
main:
    la a0, arr
    la a1, len
    call read_array

    ld a1, arr
    ld a2, len
    call solution

    ld a0, arr
    ld a1, len
    call print_array

    ld a0, arr
    call free_array

    addi a0, x0, 0
    addi a7, x0, 93
    ecall

.data
arr: .dword 0
len: .dword 0
"""
PRINT_RESULT_C = r"""
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

void print_array(int64_t *arr, int64_t len){
    for (size_t i = 0; i < len; i++) {
        fprintf(stderr, "%ld ", arr[i]);
    }
}

void read_array(int64_t **arr, int64_t *len) {
    scanf("%ld", len);

    *arr = (int64_t*)malloc(*len * sizeof(int64_t));
    if (*arr == NULL) {
        printf("internal checker error: out of memory\n");
        exit(1);
    }

    for (size_t i = 0; i < *len; i++) {
        scanf("%ld", &(*arr)[i]);
    }
}

void free_array(int64_t *arr) {
    free(arr);
}
"""


class Lab3Condition(BaseTaskClass):

    def __init__(
        self, *args,
        array_length: int = ARRAY_DEFAULT_LEN,
        condition_length: int = CONDITION_DEFAULT_LEN,
        max_length_deviation: int = DEFAULT_MAX_LENGTH_DEVIATION,
        min_value: Optional[int] = None, max_value: Optional[int] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.int_class = np.int64
        self.array_length = array_length
        self.condition_length = condition_length
        self.max_length_deviation = max_length_deviation
        self.min_value = min_value if min_value is not None else np.iinfo(self.int_class).min
        self.max_value = max_value if max_value is not None else np.iinfo(self.int_class).max
        self.task = None

        self.check_files = {
            "main.s": MAIN_S,
            "print_result.c": PRINT_RESULT_C,
        }

    def generate_task(self) -> str:
        self.task = cond_generator.Task(self.array_length, self.condition_length, self.seed)
        return TASK_DESCRIPTION.format(expression=self.task.text)

    def _generate_tests(self):
        random.seed(int(time.time()))
        np.random.seed(int(time.time()))
        self.tests = []

        compiled_object = compile(self.task.code, "<string>", "exec")
        threshold = self.int_class(self.task.threshold)
        then_number = self.int_class(self.task.then_number)
        else_number = self.int_class(self.task.else_number)
        for _ in range(self.tests_num):
            length = random.randint(self.array_length, self.array_length + self.max_length_deviation)
            arr = [np.random.randint(self.min_value, self.max_value, dtype=self.int_class) for _ in range(length)]
            input_arr = arr.copy()

            input_str = f"{length} " + " ".join(map(str, arr))
            exec(compiled_object, {  # pylint: disable=W0122
                "arr": arr,
                "threshold": threshold,
                "then_number": then_number,
                "else_number": else_number
            })
            result = " ".join(map(str, arr))

            self.tests.append(TestItem(
                input_str=input_str,
                showed_input=input_arr,
                expected=result,
                compare_func=self._compare_default
            ))

    def make_failed_test_msg(
        self, showed_input: np.ndarray, obtained: str, expected: str
    ) -> str:
        """
        showed_input is input arr
        obtained and expected are string, parsing is required
        format:
        | i | arr | Obtained | Expected | Correct |
        +---+-----+----------+----------+---------+
        | 0 |  1  |     7    |     6    |    X    |
        | 1 |  1  |     7    |     7    |    V    |
        ....
        +---+-----+----------+----------+---------+
        """
        max_int_len = max(len(str(self.min_value)), len(str(self.max_value)))
        captions = ["arr", "Obtained", "Expected"]
        is_error = False
        try:
            obtained_list = list(map(int, obtained.split(" ")))
            expected_list = list(map(int, expected.split(" ")))
        except Exception:  # pylint: disable=W0718
            is_error = True
            obtained_list = [" " for _ in range(len(showed_input))]
            expected_list = [" " for _ in range(len(showed_input))]
        correctness = [obt == exp for obt, exp in zip(obtained_list, expected_list)]
        arrs = [showed_input, obtained_list, expected_list]
        ret = self.make_array_failed_test_msg(captions, arrs, max_int_len, correctness)
        if is_error:
            ret = f"Получена ошибка при запуске '{obtained}'\n" + ret
        return ret

    def check_sol_prereq(self) -> Optional[str]:
        error = super().check_sol_prereq()
        if error is not None:
            return error
        
        if self.solution.find("ecall") != -1:
            return "Ошибка: Системные вызовы запрещены."
