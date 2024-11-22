from typing import Optional
import random
import time
import numpy as np
from riscv_course.base_module import BaseTaskClass, TestItem
from riscv_course.random_expressions.random_expressions import get_expression


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
Напишите программу на ассемблере, которая вычисляет результат математического выражения в соответствии с вариантом. Убедитесь в корректности работы программы через автоматизированную систему.

Начальные данные на момент старта программы будут расположены в регистрах a2, a3, a4 соответственно. Результат выражения должен быть сохранен в регистр a0. Порядок операций в выражении соответствует порядку операций в языке Си.

Весь код программы должен располагаться в метке solution. Программа должна заканчивать работу вызовом ret.

Шаблон программы для подготовки решения:

```
.globl solution
solution:
    # a0 = result
    ret
```

Ваше условие будет выведено ниже:
{expression}
"""
MAIN_S = r"""
.globl main
.text
main:
    la a0, x
    la a1, y
    la a2, z
    call read_data
    ld a2, x
    ld a3, y
    ld a4, z
    call solution
    call print_result_result
    addi a0, x0, 0
    addi a7, x0, 93
    ecall

.data
x: .dword 0
y: .dword 0
z: .dword 0
"""
PRINT_RESULT_C = r"""
#include<stdio.h>
#include<stdint.h>

void print_result_result(int64_t result){
    fprintf(stderr, "%ld\n", result);
}

void read_data(int64_t *a, int64_t *b, int64_t *c){
    scanf("%ld %ld %ld", a, b, c);
}
"""


class Lab1AsmInto(BaseTaskClass):

    def __init__(
        self, *args,
        a2_class: str = DEFAULT_TYPE, a3_class: str = DEFAULT_TYPE, a4_class: str = DEFAULT_TYPE,
        a2_min: Optional[int] = None, a2_max: Optional[int] = None,
        a3_min: Optional[int] = None, a3_max: Optional[int] = None,
        a4_min: Optional[int] = None, a4_max: Optional[int] = None,
        length: int = 7, minuses: float = 0.1, brackets: float = 0.8,
        operations: str = "+,-,*,&,|",
        **kwself
    ):
        super().__init__(*args, **kwself)
        self.a2_class = INT_TYPES.get(a2_class)
        if self.a2_class is None:
            raise ValueError(f"a1 register has wrong type {a2_class}")
        self.a3_class = INT_TYPES.get(a3_class)
        if self.a3_class is None:
            raise ValueError(f"a2 register has wrong type {a3_class}")
        self.a4_class = INT_TYPES.get(a4_class)
        if self.a4_class is None:
            raise ValueError(f"a3 register has wrong type {a4_class}")
        self.a2_min = a2_min
        self.a3_min = a3_min
        self.a4_min = a4_min
        self.a2_max = a2_max
        self.a3_max = a3_max
        self.a4_max = a4_max
        self.length = length
        self.minuses = minuses
        self.brackets = brackets
        self.operations = operations.split(",")
        self.expression = ""
        self.variables = ["a2", "a3", "a4"]

        self.set_minmax_values()

        self.check_files = {
            "main.s": MAIN_S,
            "print_result.c": PRINT_RESULT_C,
        }

    def set_minmax_values(self):
        # FIXME: if the cur min is below class min
        if self.a2_min is None:
            self.a2_min = np.iinfo(self.a2_class).min
        if self.a3_min is None:
            self.a3_min = np.iinfo(self.a3_class).min
        if self.a4_min is None:
            self.a4_min = np.iinfo(self.a4_class).min

        if self.a2_max is None:
            self.a2_max = np.iinfo(self.a2_class).max
        if self.a3_max is None:
            self.a3_max = np.iinfo(self.a3_class).max
        if self.a4_max is None:
            self.a4_max = np.iinfo(self.a4_class).max

    def generate_task(self) -> str:
        self.expression = get_expression(
            self.variables, self.operations, self.length, self.seed, self.minuses,
            self.brackets
        )
        return TASK_DESCRIPTION.format(expression=self.expression)

    def _generate_tests(self):
        random.seed(int(time.time()))
        self.tests = []

        compiled_expr = compile(self.expression, "<string>", "eval")

        for _ in range(self.tests_num):
            a2 = random.randint(self.a2_min, self.a2_max)
            a3 = random.randint(self.a3_min, self.a3_max)
            a4 = random.randint(self.a4_min, self.a4_max)

            a2 = self.a2_class(a2)
            a3 = self.a3_class(a3)
            a4 = self.a4_class(a4)

            result = eval(compiled_expr)  # pylint: disable=W0123
            self.tests.append(TestItem(
                input_str=f"{a2} {a3} {a4}",
                showed_input=f"a2={a2} a3={a3} a4={a4}",
                expected=str(result),
                compare_func=self._compare_default
            ))
    
    def check_sol_prereq(self) -> Optional[str]:
        error = super().check_sol_prereq()
        if error is not None:
            return error
        
        if self.solution.find("ecall") != -1:
            return "Ошибка: Системные вызовы запрещены."
