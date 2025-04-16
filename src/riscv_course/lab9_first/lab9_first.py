from typing import Optional
import random
import numpy as np
from ..base_module import BaseTaskClass, TestItem
from .lab9_gen import start_gen

DEFAULT_TYPE = "int64"
INT_TYPES = {
    "int64":  np.int64,
    "int32":  np.int32,
    "int16":  np.int16,
    "int8":   np.int8,
    "uint64": np.uint64,
    "uint32": np.uint32,
    "uint16": np.uint16,
    "uint8":  np.uint8
}
TASK_DESCRIPTION = """
Вам предоставлена сломанная программа которая, ваша задача найти в чем ошибка в коде, и исправить его, чтобы программа выводила SUCCESS.
Для решения требуется чтобы условие t3 == t4 было истинно. Изначально t4 = 0.  Загрузите исправленный код для проверки.

Ваша функйия с ошибкой:   

"""

MAIN_S = r"""
.data
    error: .asciz "Access denied!"
    flag: .asciz "SUCCESS"

.globl main  
.text
main:
    li t1, 0x944f
    li t2, 0xf10
    li t4, 0x0  # ожидаемое значение t4

    call solution  # вызов внешней функции с логикой

final:
    bne t3, t4, fail  # если t3 != t4 fail
    j success         # если t3 == t4 success

fail:
    li a0, 1
    la a1, error
    li a2, 14
    li a7, 64
    ecall
    j exit

success:
    li a0, 1
    la a1, flag
    li a2, 7
    li a7, 64
    ecall

exit:
    li a7, 93
    li a0, 0
    ecall
"""

PRINT_RESULT_C = r"""
#include<stdio.h>
#include<stdint.h>

void print_result(int64_t result){
    fprintf(stderr, "%ld\n", result);
}

void read_data(int64_t *a, int64_t *b){
    scanf("%ld %ld", a, b);
}
"""


class Lab9First(BaseTaskClass):

    def __init__(
            self, *args,
            n: int,
            deep: int,
            student_id: int,
            **kwself
    ):
        super().__init__(*args, **kwself)
        self.asm_code = start_gen(n=n, deep=deep, student_id=student_id)
        self.expected_result = 'SUCCESS'
        self.wrond_result = 'Access denied'
        self.check_files = {
            "main.s": MAIN_S,
            "print_result.c": PRINT_RESULT_C,
        }

    def generate_task(self) -> str:
        return TASK_DESCRIPTION + self.asm_code

    def _generate_tests(self):
        random.seed(42)
        self.tests = []
        self.tests.append(TestItem(
            input_str=f"",
            showed_input=f"",
            expected=str("SUCCESS"),
            compare_func=self._compare_default
        ))

    def check_sol_prereq(self) -> Optional[str]:
        error = super().check_sol_prereq()
        if error is not None:
            return error

        if self.solution.find("ecall") != -1:
            return "Ошибка: Системные вызовы запрещены."
