import os
from typing import Optional
import random
import numpy as np
from riscv_course.base_module import BaseTaskClass, TestItem
import riscv_course.random_expressions.random_expressions as generator
import riscv_course.int_utils as int_utils

DEFAULT_BINARY_OPERATIONS = ["+", "-", "^", "&", "|"]
DEFAULT_LENGTH = 2
DEFAULT_MINUSES_THRESHOLD = 0.1
DEFAULT_BRACKETS_THRESHOLD = 0.8
DEFAULT_N_CALLS_PER_TEST = 5
DEFAULT_N_ENTRIES_AT_START = 5

TASK_DESCRIPTION = """
Требуется написать программу, которая:
* реализует функцию-обработчик (метка *on_event*) прерывания в виде вызываемой процедуры;
* в метке *load* подключает обработчик, размещая его адрес в таблице обработчиков, дописывая строку в ближайшую свободную строку (гарантируется, что хотя бы одна такая есть);
* в рамках обработчика реализует вычисления согласно заданию, а также обновление счетчика вызовов в таблице;
* в метке *unload* отключает обработчик (удаляя его строку из таблицы).

В качестве **исходных данных** дается стартовый адрес таблицы обработчиков (в метке *listener_table*),  а также формула для вычислений с аргументами.

Таблица обработчиков имеет вид массива с элементами по 10 байт следующей структуры:

| Адрес | Описание                       | Описание                                                 |
|:------|:-------------------------------|:---------------------------------------------------------|
| 0     | Не используется (6 байт)       | Количество строк в таблице не считая заголовок (4 байта) |
| 10    | Адрес обработчика №1 (8 байт)  | Количество вызовов обработчика №1  (2 байта)             |
| ...   | ...                            | ...                                                      |
| 10*N  | Адрес обработчика № N (8 байт) | Количество вызовов обработчика № N  (2 байта)            |

Обработчик должен иметь метку *on_event*. Аргументы обработчика передаются через три адреса в памяти, задаваемые метками *a*,*b*,*c*. Результат выполнения обработчика должен быть размещен в регистре *a0*.  Обработчик должен самостоятельно увеличивать счетчик вызовов из таблицы обработчиков. 

Расположение входных данных в памяти:
* Метка a указывает на {a_type}
* Метка b указывает на {b_type}
* Метка c указывает на {c_type}

Результат выполнения обработчика должен иметь следующий тип данных: {result_type}

Ваша программа должна иметь следующую структуру:

```
.globl load
.globl unload
load: 
    # подключите ваш обработчик события
    ret
 
# ваш обработчик события для нажатия на кнопку
on_event:
    # Обработайте событие ...
    ret

unload:
    # Отключите ваш обработчик (если он содержится в таблице)...
    ret
```

Ваше выражение:
{expression}
"""

MAIN_CPP = open(os.path.dirname(os.path.realpath(__file__)) + "/main.cpp").read()

class Lab6Interrupt(BaseTaskClass):
    def __init__(
        self,
        a_type, b_type, c_type, result_type,
        a_min, a_max, b_min, b_max, c_min, c_max,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.task = None
        self.a_type, self.a_min, self.a_max = int_utils.numpify_int_type(a_type, a_min, a_max)
        self.b_type, self.b_min, self.b_max = int_utils.numpify_int_type(b_type, b_min, b_max)
        self.c_type, self.c_min, self.c_max = int_utils.numpify_int_type(c_type, c_min, c_max)
        self.result_type = int_utils.INT_TYPES[result_type]

        self.a_ctype = int_utils.get_ctype_name(a_type)
        self.b_ctype = int_utils.get_ctype_name(b_type)
        self.c_ctype = int_utils.get_ctype_name(c_type)
        self.result_ctype = int_utils.get_ctype_name(result_type)

        self.check_files = {
            "main.cpp": MAIN_CPP
        }

    def generate_task(self):
        variables = ["a", "b", "c"]
        self.task = generator.get_expression(variables, DEFAULT_BINARY_OPERATIONS, DEFAULT_LENGTH, self.seed, DEFAULT_MINUSES_THRESHOLD, DEFAULT_BRACKETS_THRESHOLD, "-", True)
        return TASK_DESCRIPTION.format(
            expression=self.task,
            a_type=int_utils.INT_TYPE_DESCRIPTION[self.a_type],
            b_type=int_utils.INT_TYPE_DESCRIPTION[self.b_type],
            c_type=int_utils.INT_TYPE_DESCRIPTION[self.c_type],
            result_type=int_utils.INT_TYPE_DESCRIPTION[self.result_type]
        )

    def _generate_tests(self):
        random.seed(self.seed)
        self.tests = []

        compiled_object = compile(self.task, "<string>", "eval")

        for _ in range(self.tests_num):
            test_numbers = [ DEFAULT_N_ENTRIES_AT_START + random.randint(-1, 1), DEFAULT_N_CALLS_PER_TEST ]
            for __ in range(DEFAULT_N_CALLS_PER_TEST):
                a = self.a_type(random.randint(self.a_min, self.a_max))
                b = self.b_type(random.randint(self.b_min, self.b_max))
                c = self.c_type(random.randint(self.c_min, self.c_max))

                # DeprecationWarning: NumPy will stop allowing conversion of out-of-bound Python integers to integer arrays.
                # For the old behavior, usually: np.array(value).astype(dtype) will give the desired result (the cast overflows).
                res = np.array(eval(compiled_object)).astype(self.result_type) 
                test_numbers += [a, b, c, int(res)]
                
            test_str = ' '.join(map(str, test_numbers))
            self.tests.append(TestItem(
                input_str=test_str,
                showed_input='see text below',
                expected='',
                compare_func=self._compare_default
            ))
    
    def compile(self):
        return self._compile_internal(
            compiler="riscv64-unknown-linux-gnu-g++",
            compile_args=f"-static -DA_TYPE={self.a_ctype} -DB_TYPE={self.b_ctype} -DC_TYPE={self.c_ctype} -DRESULT_TYPE={self.result_ctype}"
        )

    def check_sol_prereq(self) -> Optional[str]:
        lines = self.solution.splitlines()

        if len(lines) == 0:
            return "Ошибка: пустой файл."

        if self.solution.find(".globl load") == -1:
            return "Ошибка: для метки load не определена видимость за границами файла с помощью директивы .globl"
        if self.solution.find(".globl unload") == -1:
            return "Ошибка: для метки unload не определена видимость за границами файла с помощью директивы .globl"

        if self.solution.find("load:") == -1:
            return "Ошибка: Метка load не найдена."
        if self.solution.find("unload:") == -1:
            return "Ошибка: Метка unload не найдена."
        if self.solution.find("on_event:") == -1:
            return "Ошибка: Метка on_event не найдена."

        return None  # check is passed

    def run_tests(self) -> tuple[bool, str]:
        msgs = []
        for t in self.tests:
            if (result := self.run_solution(t)) is not None:
                msgs.append(result[0])
                if self.fail_on_first:
                    break

        if len(msgs) == 0:
            return True, "OK"
        return False, "\n".join(msgs)
