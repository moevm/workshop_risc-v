from typing import Optional
import os
from riscv_course.base_module import BaseTaskClass, TestItem
from riscv_course.random_asm_generator.utils import MODE_GENERATE, \
    MODE_VALIDATE, generate_random_source_simple


TASK_DESCRIPTION = """
Дан бинарный исполняемый файл prog.x, скомпилированный с отладочной информацией (флаг -g). Данный файл реализует случайную, но работоспособную программу для подсчетов.

Вам необходимо провести отладку программы с помощью gdb и определить:
1. В какой момент регистру a0 намеренно присваивается значение 0? Обратите внимание, что процесс присвоения данного значения будет выполнен не в лоб (a0 = 0), а через инструкции, включающие другие регистры, но гарантированно всегда передающие 0 в a0.
2. Каким является значение a0 ДО момента из пункта №1 ?

Значение регистра a0  из пункта №2 является ответом на данное задание. Зафиксируйте его и введите при запуске

docker run --rm -it riscvcourse/workshop_risc-v lab2_debug --mode check --seed <seed>

Ниже вас ждет терминал для отладки, в котором вам будут доступны утилиты riscv64-unknown-linux-gnu-gcc, qemu-riscv64 и riscv64-unknown-linux-gnu-gdb.
"""
PRINT_RESULT_C = r"""
#include <stdio.h>

void print_result(int result){
   fprintf(stderr, "%d", result);
}
"""

DEFAULT_START_SECTION_LEN = 10
DEFAULT_END_SECTION_LEN = 4


class Lab2Debug(BaseTaskClass):

    def __init__(
        self, *args,
        starting_section_length: int = DEFAULT_START_SECTION_LEN,
        ending_section_length: int = DEFAULT_END_SECTION_LEN,
        answer: str = "",
        interactive: bool = False, print_task_when_i: bool = True,
        **kwself
    ):
        super().__init__(*args, **kwself)
        self.starting_section_length = starting_section_length
        self.ending_section_length = ending_section_length
        self.interactive = interactive
        self.print_task_when_i = print_task_when_i
        self.answer = answer

        self.check_files = {
            "print_result.c": PRINT_RESULT_C,
        }

    def load_student_solution(
        self, solfile: Optional[str] = None, solcode: Optional[str] = None
    ):
        # Do nothing, pass solution (answer) as argument
        pass

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

    def generate_task(self) -> str:
        main_s = generate_random_source_simple(
            self.starting_section_length, self.ending_section_length,
            MODE_GENERATE, self.seed,
        )
        if (err := self.__compile_binary(main_s)) is not None:
            return err
        return TASK_DESCRIPTION

    def init_task(self) -> str:
        task_descp = super().init_task()
        if self.interactive:
            if self.print_task_when_i:
                print(task_descp)
            os.system("rm -rf main.py pyproject.toml requirements.txt src sol.s main.s print_result.c")
            os.execlp("bash", "-c")
        return task_descp

    def run_tests(self) -> tuple[bool, str]:
        main_s = generate_random_source_simple(
            self.starting_section_length, self.ending_section_length,
            MODE_VALIDATE, self.seed,
        )
        self.check_files["main.s"] = main_s.replace("_start", "main")
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
        correct_answer = res[0]  # program output
        if self.answer.strip() == correct_answer.strip():
            return True, "OK"
        return False, "Wrong answer"

    def _generate_tests(self):
        pass
