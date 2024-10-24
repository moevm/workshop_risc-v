from typing import Optional
from dataclasses import dataclass
import random
import time
import numpy as np
from riscv_course.base_module import BaseTaskClass, TestItem
import riscv_course.random_expressions.random_expressions as generator
import os
import subprocess
import shlex

DEFAULT_BINARY_OPERATIONS = ['&', '|', '^']
DEFAULT_LENGTH = 2
DEFAULT_MINUSES_THRESHOLD = 0.1
DEFAULT_BRACKETS_THRESHOLD = 0.8
DEFAULT_N_STATES_PER_TEST = 5

TASK_DESCRIPTION = """
Требуется написать программу, которая 
* реализует цикл активного ожидания для обработки событий;
* в рамках цикла отслеживает состояние кнопок и также изменяет состояние светодиодов.

В качестве исходных данных дается правило, по которому необходимо зажигать светодиоды в зависимости от состояний кнопок. Изначально все светодиоды выключены.

Считаем, что в системе есть 8 светодиодов и 8 кнопок. Кнопки и светодиоды нумеруются с нуля. У каждого светодиода и кнопки есть бинарное состояние, задаваемое через int:
1 - светодиод горит (кнопка нажата),
0 - светодиод не горит (кнопка не нажата).

Вспомогательные процедуры, которые вам необходимо использовать:
int get_button_status (int button_number)
void set_led_status (int led_number, int led_status)
void delay()

Ваша программа должна иметь следующую структуру:

```
.globl solution
solution: 
      

    ret
```

Ваше задание:
{expression}
"""

LED_CPP = open(os.path.dirname(os.path.realpath(__file__)) + "/led.cpp").read()

@dataclass
class Task:
    code: str
    text: str

class Lab5Daemon(BaseTaskClass):
    def __init__(
        self, *args,
        interactive: bool,
        time_scale: float,
        n_buttons: int,
        n_leds: int,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.interactive = interactive
        self.time_scale = time_scale
        self.n_buttons = n_buttons
        self.n_leds = n_leds
        self.task = None

        self.check_files = {
            "led.cpp": LED_CPP
        }

    def generate_task(self):
        variables = [f"buttons[{i}]" for i in range(self.n_buttons)]
        code = []
        
        cur_seed = self.seed
        for i in range(self.n_leds):
            expr = generator.get_expression(variables, DEFAULT_BINARY_OPERATIONS, DEFAULT_LENGTH, cur_seed, DEFAULT_MINUSES_THRESHOLD, DEFAULT_BRACKETS_THRESHOLD, "not ")
            code.append(f"leds[{i}] = " + expr)
            cur_seed = random.randint(0, 2**32)
        
        code_str = '\n'.join(code)
        text_str = code_str.replace(']', '').replace('buttons[', 'X').replace('leds[', 'Y')
        self.task = Task(code_str, text_str)
        return TASK_DESCRIPTION.format(expression=self.task.text)

    def _generate_tests(self):
        random.seed(self.seed)
        self.tests = []

        compiled_object = compile(self.task.code, "<string>", "exec")

        for _ in range(self.tests_num):
            test_input = [DEFAULT_N_STATES_PER_TEST]
            for __ in range(DEFAULT_N_STATES_PER_TEST):
                buttons_bits = random.randrange(0, 2**self.n_buttons)
                buttons = []
                for i in range(self.n_buttons):
                    buttons.append((buttons_bits >> i) & 1)
                
                leds = [0] * self.n_leds
                exec(compiled_object)
                
                expected_leds_bits = 0
                for i in range(self.n_leds):
                    expected_leds_bits |= ((1 if leds[i] else 0) << i)

                test_input += [buttons_bits, expected_leds_bits]
            
            test_str = ' '.join(map(str, test_input))
            self.tests.append(TestItem(
                input_str=test_str,
                showed_input='see logs below',
                expected='',
                compare_func=self._compare_default
            ))
    
    def compile(self):
        return self._compile_internal(
            compiler="riscv64-unknown-linux-gnu-g++",
            compile_args=f"-static -DTIME_SCALE={self.time_scale} -DN_LEDS={self.n_leds} -DN_BUTTONS={self.n_buttons}"
        )
    
    def check_sol_prereq(self) -> Optional[str]:
        lines = self.solution.splitlines()

        if len(lines) == 0:
            return "Ошибка: пустой файл."

        if lines[0].find(".globl solution") == -1:
            return "Ошибка: для метки solution не определена видимость за границами файла."

        if self.solution.find("solution:") == -1:
            return "Ошибка: Метка solution не найдена."

        return None  # check is passed

    def run_tests(self) -> tuple[bool, str]:
        if self.interactive:
            os.system("qemu-riscv64 prog.x interactive")
            return False, "Интерактивный режим завершил работу"
        
        msgs = []
        for t in self.tests:
            if (result := self.run_solution(t)) is not None:
                msgs.append(result[0])
                if self.fail_on_first:
                    break

        if len(msgs) == 0:
            return True, "OK"
        return False, "\n".join(msgs)
