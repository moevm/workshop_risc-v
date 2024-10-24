import random
from typing import Optional
from riscv_course.base_module import BaseTaskClass, TestItem
from riscv_course.base_module.base_task import FAILED_TEST_MSG
import riscv_course.random_expressions.string_operations as task_generator

DEFAULT_MIN_TEST_LENGTH = 100
DEFAULT_MAX_TEST_LENGTH = 125
DEFAULT_NUM_OPERATIONS  = 3


TASK_DESCRIPTION = """
Требуется написать программу, которая считывает строку из потока ввода, преобразует строку в памяти. Результатом выполнения вашей программы будет измененная строка, выведенная в консоль.

В качестве исходных данных дается набор действий для преобразования строки. 
Ваша программа должна иметь следующую структуру:

```
.globl main
.text
main: 
     
    # считайте строку 
    
    # преобразуйте строку

    # выведите строку в консоль


    # завершение работы программы
    addi a0, x0, 0
    addi a7, x0, 93
    ecall    
```


Внимание, для выполнения данного задания вам с большой вероятностью потребуется менять размер исходной строки - она может стать как длиннее, так и короче. 

В финале работы вашей программы вам необходимо вывести всю строку в консоль через системный вызов write (подробнее про [syscalls in linux](https://jborza.com/post/2021-05-11-riscv-linux-syscalls/)), в stdout.
Ваш список преобразований строки будет выведен ниже (ваша программа должна выполнять преобразования в указанном порядке):
{your_task}
"""

LAB4_FAILED_MSG = FAILED_TEST_MSG + "\n\nObtained input with highlighted non-ascii chars: '{non_ascii}'"


def has_ecall(line: str):
    if '#' in line:
        line = line[:line.find('#')]
    commands = line.split(';')
    commands = map(lambda x: x.strip(), commands)
    return 'ecall' in commands


class Lab4String(BaseTaskClass):
    def __init__(
        self, *args,
        min_test_length: int = DEFAULT_MIN_TEST_LENGTH,
        max_test_length: int = DEFAULT_MAX_TEST_LENGTH,
        num_operations: int = DEFAULT_NUM_OPERATIONS,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.min_test_length = min_test_length
        self.max_test_length = max_test_length
        self.num_operations  = num_operations
        self.operations = None
        self.check_files = {}
    
    def generate_task(self) -> str:
        self.operations = task_generator.generate_operations(self.seed, self.num_operations)
        text = task_generator.generate_text(self.operations)
        return TASK_DESCRIPTION.format(your_task=text)

    def _generate_tests(self):
        random.seed(self.seed)
        self.tests = []

        for _ in range(self.tests_num):
            input_str = task_generator.generate_input_string(
                    self.operations,
                    self.min_test_length,
                    self.max_test_length
            )

            result = task_generator.apply_operations(input_str, self.operations)

            self.tests.append(TestItem(
                input_str=input_str,
                showed_input=input_str,
                expected=result,
                compare_func=self._compare_default
            ))
    
    def check_sol_prereq(self) -> Optional[str]:
        lines = self.solution.splitlines()
        
        if len(lines) == 0:
            return "Ошибка: пустой файл."

        if lines[0].find(".globl main") == -1:
            return "Ошибка: для метки main не определена видимость за границами файла."

        if self.solution.find("main:") == -1:
            return "Ошибка: Метка main не найдена."

        if not any(map(has_ecall, lines)):
            return "Ошибка: Инструкция ecall не найдена."
        
        return None

    def make_failed_test_msg(
        self, showed_input: str, obtained: str, expected: str
    ) -> str:
        return LAB4_FAILED_MSG.format(
            inp=showed_input,
            obt=obtained,
            exp=expected,
            non_ascii=str(obtained.encode())[2:-1],
        )
