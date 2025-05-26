from typing import Optional
import random
import numpy as np
from ..base_module import BaseTaskClass, TestItem
from .lab8_gen import GenerateLab8

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
Проанализируйте программу на ассемблере RISC-V, которая создает граф вызовов функций и вычисляет итоговое значение в соответствии с вашим вариантом.

Исходный код программы будет сгенерирован автоматически на основе вашего ID. 
Ваша задача - проанализировать последовательность вызовов функций и операции с регистрами, чтобы определить итоговое значение, которое должно быть записано в регистр a5.

Сгенерированная программа для анализа:
{asm_code}
"""

PRINT_RESULT_C = r"""
#include<stdio.h>
#include<stdint.h>

void print_result(int64_t result){
    fprintf(stderr, "%ld\n", result);
}
"""

DEFAULT_START_LEN = 12
DEFAULT_DEEP = 0.5

class Lab8Branch(BaseTaskClass):
    def __init__(
        self, *args,
        n: int = DEFAULT_START_LEN,
        deep: float = DEFAULT_DEEP,
        answer: str = "",
        **kwself
    ):
        super().__init__(*args, **kwself)
        self.generator = GenerateLab8(n=n, deep=deep, id=self.seed).generate_asm()
        self.expected_result = self.generator[0]
        self.asm_code = self.generator[1]
        self.answer = answer
        self.n = n
        self.deep = deep
        self.check_files = {
            "print_result.c": PRINT_RESULT_C,
        }
    
    def load_student_solution(
    self, solfile: Optional[str] = None, solcode: Optional[str] = None):
        self.answer = solcode
    # Do nothing, pass solution (answer) as argument
        pass


    def generate_task(self) -> str:
        main_s = self.asm_code
        if (err := self.__compile_binary(main_s)) is not None:
            return err
        return TASK_DESCRIPTION + self.asm_code


    def check_sol_prereq(self) -> Optional[str]:
        return None


    def compile(self) -> Optional[str]:
        return None


    def __compile_binary(self, src: str) -> Optional[str]:
        t_files = self.check_files
        self.check_files = {"main.s": src}
        self.solution = ""
        if (err := self._compile_internal(compile_args="-nostdlib -static -g")) is not None:
            return f"Bad source code generated. Error: {err}.\n" \
                    "Contact to the authors to solve the problem"
        self.check_files = t_files
        return None
    
    def run_tests(self) -> tuple[bool, str]:
        self.check_files["main.s"] = self.asm_code.replace("_start", "main")
        self.solution = ""
        if (err := self._compile_internal(compile_args="-static")) is not None:
            return (False, f"Bad source code generated. Error: {err}.\n"
                            "Contact to the authors to solve the problem"
                    )

        dummy_test = TestItem(
            input_str="", showed_input="",
            expected="text", compare_func=self._compare_default
        )
        res = self._run_solution_internal(dummy_test)
        if res is None:
            return (False, "Bad source code generated.\n"
                            "Contact to the authors to solve the problem"
                    )

        if self.answer.strip() == str(self.expected_result).strip():
            return True, "OK"
        return False, f"Wrong answer"

    def _generate_tests(self):
        pass
