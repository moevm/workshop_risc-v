import random
from typing import Optional
import numpy as np
from riscv_course.base_module import BaseTaskClass, TestItem
from riscv_course.random_expressions.random_expressions import get_expression


DEFAULT_MAX_LENGTH_DEVIATION = 30
ARRAY_DEFAULT_LEN = 70

TASK_DESCRIPTION = """
Требуется написать программу, которая использует векторные инструкции для поэлементной обработки массивов по заданной формуле.

В качестве исходных данных даются стартовые адреса в памяти, в которых хранятся массивы, количество элементов в массивах и формула для требуемых вычислений (Вычисления производятся над массивами поэлементно). Порядок операций в формуле соответствует порядку операций в языке Си. 

При автоматической проверке вашей программы исходные данные располагаются в регистрах следующим образом:
  - a0 - адрес памяти, где расположен массив arr1
  - a1 - адрес памяти, где расположен массив arr2
  - a2 - адрес памяти, где расположен массив arr3
  - a3 - адрес памяти, где расположен массив arr4
  - a4 - количество элементов в массивах (гарантируется, что во всех массивах одинаковое количество элементов)
  - a5 - адрес памяти, где расположен массив res, в который требуется записать результат поэлементных вычислений
Массивы arr1-arr4 уже заполнены данными.

Ваша программа должна иметь следующую структуру:
```
.globl solution
solution:
    # при старте данной метки ваша программа должна выполнить 
    # поэлементные векторные вычисления по заданной формуле
    ret
```

Доступ к массивам (чтение, запись) должен выполняться из памяти. Предполагайте, что в запускаем окружение размер векторного регистра составляет 256 бит, максимальный размер одного элемента 64 бита, а массивы состоят 32-х битных чисел.

Формула для вычислений будет выведена ниже:
{expression}
"""
MAIN_C = r"""
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>

#define MAXARRS (4)

void solution(uint32_t *, uint32_t *, uint32_t *, uint32_t *, int, uint32_t *);

void print_array(int length, uint32_t *array){
    for (int i=0; i < length; i++){
        fprintf(stderr,"%" SCNd32 " ", array[i]);
    }
}

void read_array(uint32_t length, uint32_t *array){
    for (int i=0; i < length; i++){
        scanf("%" SCNd32, array + i);
    }
}

int main(){
    uint32_t *arrs[MAXARRS] = {0};
    uint32_t *res;
    int len;
    scanf("%d", &len);
    for(int i = 0; i < MAXARRS; i++){
        arrs[i] = malloc(len * sizeof(uint32_t));
        read_array(len, arrs[i]);
    }
    res = malloc(len * sizeof(uint32_t));
    solution(arrs[0], arrs[1], arrs[2], arrs[3], (int) len, (uint32_t*) res);
    print_array(len, res);
    free(res);
    for(int i = 0; i < MAXARRS; i++){
        free(arrs[i]);
    }
    return 0;
}
"""


class Lab7Vectors(BaseTaskClass):
    def __init__(
        self, *args,
        array_length: int = ARRAY_DEFAULT_LEN,
        max_length_deviation: int = DEFAULT_MAX_LENGTH_DEVIATION,
        min_value: Optional[int] = None, max_value: Optional[int] = None,
        length: int = 7, minuses: float = 0.1, brackets: float = 0.5,
        operations: str = "+,-,*,&,|",
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.vector_instructions = (
            "vadd", "vaddi", "vsub", "vmul", "vdiv", "vsl", "vsr", "vand",
            "vor", "vxor",
        )
        self.length = length
        self.minuses = minuses
        self.brackets = brackets
        self.operations = operations.split(",")
        self.expression = ""
        self.variables = [f"arr{i}" for i in range(1, 5)]
        self.elem_class = np.int32
        self.array_length = array_length
        self.max_length_deviation = max_length_deviation
        self.min_value = min_value if min_value is not None else np.iinfo(self.elem_class).min
        self.max_value = max_value if max_value is not None else np.iinfo(self.elem_class).max

        self.check_files = {
            "main.c": MAIN_C,
        }

    def check_sol_prereq(self) -> Optional[str]:
        if (ret := super().check_sol_prereq()) is not None:
            return ret

        if self.solution.find("vsetvli") == -1:
            return "Не обнаружено конфигурирующей векторной инструкции vsetvli"

        if self.solution.find("vle32") == -1:
            return "Не обнаружено векторной 32-х битной инструкции для загрузки элементов"

        if self.solution.find("vse32") == -1:
            return "Не обнаружено векторной 32-х битной инструкции для сохранения элементов"

        if all(self.solution.find(inst) == -1
                for inst in self.vector_instructions):
            return "Не обнаружено векторной инструкции для обработки элементов"

        return None

    def generate_task(self) -> str:
        self.expression = get_expression(
            self.variables, self.operations, self.length, self.seed,
            self.minuses, self.brackets,
        )
        return TASK_DESCRIPTION.format(expression=self.expression)

    def compile(self) -> Optional[str]:
        return self._compile_internal(compile_args="-march=rv64iv -static")

    def run_solution(self, test: TestItem) -> Optional[str]:
        return self._run_solution_internal(
            test, emu_args="-cpu rv64,v=true,vlen=256,elen=64,vext_spec=v1.0",
        )

    def _generate_tests(self):
        random.seed(self.seed)
        self.tests = []

        for _ in range(self.tests_num):
            arr_len = random.randint(
                self.array_length,
                self.array_length + self.max_length_deviation
            )
            arrs = np.random.randint(
                self.min_value, self.max_value, dtype=self.elem_class,
                size=(4, arr_len)
            )

            input_str = f"{arr_len} " + "\n".join([
                " ".join(str(x) for x in arr)
                for arr in arrs
            ])

            arr1, arr2, arr3, arr4 = arrs  # pylint: disable=W0612
            res_arr = eval(self.expression)  # pylint: disable=W0123

            result = " ".join(map(str, res_arr))

            self.tests.append(TestItem(
                input_str=input_str,
                showed_input=arrs,
                expected=result,
                compare_func=self._compare_default
            ))

    def make_failed_test_msg(
        self, showed_input: np.ndarray, obtained: str, expected: str
    ) -> str:
        """
        showed_input is arrs (four arrays)
        obtained and expected are string, parsing is required
        format:
        | i | arr1 | arr2 | arr3 | arr4 | Obtained | Expected | Correct |
        +---+------+------+------+------+----------+----------+---------+
        | 0 |  1   |  2   |  3   |  5   |     7    |     6    |    X    |
        | 1 |  1   |  3   |  3   |  5   |     7    |     7    |    V    |
        ....
        +---+------+------+------+------+----------+----------+---------+
        """
        max_int_len = max(len(str(self.min_value)), len(str(self.max_value)))
        captions = [f"arr{i + 1}" for i in range(len(showed_input))] + ["Obtained", "Expected"]
        is_error = False
        try:
            obtained_list = list(map(int, obtained.split(" ")))
            expected_list = list(map(int, expected.split(" ")))
        except Exception:  # pylint: disable=W0718
            is_error = True
            obtained_list = [" " for _ in range(len(showed_input[0]))]
            expected_list = [" " for _ in range(len(showed_input[0]))]
        correctness = [obt == exp for obt, exp in zip(obtained_list, expected_list)]
        arrs = [*showed_input, obtained_list, expected_list]
        ret = self.make_array_failed_test_msg(captions, arrs, max_int_len, correctness)
        if is_error:
            ret = f"Получена ошибка при запуске '{obtained}'\n" + ret
        return ret
