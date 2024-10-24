from typing import Optional, Callable
import enum 
import os
import subprocess
import shlex
from dataclasses import dataclass


COMPILE_TIMEOUT = 60
RUN_TIMEOUT = 5

FAILED_TEST_MSG = "Test is failed.\nInput: '{inp}'\nObtained: '{obt}'.\nExpected: '{exp}'"

DEFAULT_TEST_NUM = 50


@dataclass
class TestItem:
    input_str: str
    showed_input: str
    expected: str
    compare_func: Callable[[str, str], bool]


class BaseTaskClass:

    def __init__(
        self, compile_name: str = "prog.x", seed: int = 0,
        tests_num: int = DEFAULT_TEST_NUM, fail_on_first_test: bool = True,
        array_align: str = "center", jail_exec: str = "chroot",
        jail_path: Optional[str] = None,
    ):
        self.solution = ""
        self.check_files = {}
        self.prog_name = compile_name
        self.seed = seed
        self.tests_num = tests_num
        self.tests: list[TestItem] = []
        self.compile_timeout = COMPILE_TIMEOUT
        self.run_timeout = RUN_TIMEOUT
        self.fail_on_first = fail_on_first_test
        self._array_align = array_align
        self.jail_exec = jail_exec
        self.jail_path = jail_path if jail_path is not None else os.environ.get("JAIL_PATH", "")

    def load_student_solution(self, solfile: Optional[str] = None, solcode: Optional[str] = None):
        if solcode is None and solfile is None:
            raise ValueError("Neither solcode nor solfile is provided")
        if solcode is not None and solfile is not None:
            raise ValueError("Both solcode and solfile are provided")
        if solcode is not None:
            self.solution = solcode
        elif solfile is not None:
            if not os.path.exists(solfile):
                raise ValueError("Ошибка: Файл решения не найден.")
            with open(solfile, "r", encoding="utf-8") as f:
                self.solution = f.read().strip()

    def check_sol_prereq(self) -> Optional[str]:
        """
        This is counter-intuitive, but more straightforward than other ways:
        on success it returns None, on failure it returns str with an error
        """
        lines = self.solution.splitlines()

        if len(lines) == 0:
            return "Ошибка: пустой файл."

        if lines[0].find(".globl solution") == -1:
            return "Ошибка: для метки solution не определена видимость за границами файла."

        if self.solution.find("solution:") == -1:
            return "Ошибка: Метка solution не найдена."

        if lines[-1].find("ret") == -1:
            return "Ошибка: Инструкция ret не найдена."

        return None  # check is passed

    def _compile_internal(
        self, solution_name: str = "sol.s",
        compiler: str = "riscv64-unknown-linux-gnu-gcc",
        compile_args: str = "-static",
    ) -> Optional[str]:
        """
        General method to compile work
        Return value is the same as in `check_sol_prereq` method
        """
        # Dump files into filesystem
        for name, content in self.check_files.items():
            with open(name, "w", encoding="utf-8") as f:
                f.write(content)

        with open(solution_name, "w", encoding="utf-8") as f:
            f.write(self.solution)
            f.write("\n")

        compile_command = f"{compiler} {compile_args} "\
            f"{' '.join(name for name in self.check_files.keys())} "\
            f"{solution_name} -o {os.path.join(self.jail_path, self.prog_name)}"
        p = subprocess.run(
            shlex.split(compile_command),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=self.compile_timeout, check=False,
        )
        if p.returncode != 0:
            return f"Ошибки при компиляции решения:\n{p.stdout.decode()}"

        return None  # compile is success

    def compile(self) -> Optional[str]:
        """
        Derived classes must override this method
        """
        return self._compile_internal()

    def generate_task(self) -> str:
        return "TODO: Base class"

    def _generate_tests(self):
        pass

    def _run_solution_internal(
        self, test: TestItem,
        emulator: str = "qemu-riscv64", emu_args: str = "", prog_args: str = "",
    ) -> Optional[tuple[str, str]]:
        """
        check_func: takes two arguments -- input and obtained output -- and
        returns None if the test passes, otherwise returns expected output
        """
        if self.jail_path != "":
            emulator = "/" + emulator
        run_command = f"{self.jail_exec} {self.jail_path} "\
            f"{emulator} {emu_args} {self.prog_name} {prog_args}"
        try:
            p = subprocess.run(
                shlex.split(run_command),
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                input=test.input_str.encode(),
                timeout=self.run_timeout, check=False,
            )
        except subprocess.TimeoutExpired as te:
            return (f"Выполнение программы превысило ограничение в {te.timeout} секунд",
                    f"Программа выполняется менее {te.timeout} секунд")
        output = p.stderr.decode().strip() + p.stdout.decode().strip()
        if p.returncode != 0:
            return (f"Программа завершилась с кодом {p.returncode}. Вывод:\n{output}",
                    "Программа завершилась с кодом 0 ")
        passed = test.compare_func(output, test.expected)
        if passed:
            return None
        return output, test.expected

    def _compare_default(self, input_str: str, obtained: str) -> bool:
        return input_str.strip() == obtained.strip()

    def run_solution(self, test: TestItem) -> Optional[str]:
        return self._run_solution_internal(test)

    def make_failed_test_msg(
        self, showed_input: str, obtained: str, expected: str
    ) -> str:
        return FAILED_TEST_MSG.format(
            inp=showed_input,
            # obt=str(result[0].encode())[2:-1], # dirty hack to make non-ascii characters visible
            obt=obtained,
            exp=expected
        )

    def run_tests(self) -> tuple[bool, str]:
        msgs = []
        for t in self.tests:
            if (result := self.run_solution(t)) is not None:
                msgs.append(self.make_failed_test_msg(
                    t.showed_input, result[0], result[1]
                ))
                if self.fail_on_first:
                    break

        if len(msgs) == 0:
            return True, "OK"
        return False, "\n".join(msgs)

    # ======== Pipeline methods ========
    def init_task(self) -> str:
        return self.generate_task()

    def check(self) -> tuple[bool, str]:
        """
        Run checks on loaded solution. ***Important***:
        `load_student_solution` must be called before this method
        """

        def __ret_err(msg: str, prefix: str = "") -> tuple[bool, str]:
            return False, f"{prefix}{msg}"

        try:
            if (msg := self.check_sol_prereq()) is not None:
                return __ret_err(msg)
            if (msg := self.compile()) is not None:
                return __ret_err(msg)
            self.generate_task()
            self._generate_tests()
            return self.run_tests()
        except Exception as e:  # pylint: disable=W0718
            return __ret_err(str(e), "Непредвиденная ошибка во время проверки решения: ")

    def make_array_failed_test_msg(
        self, caption: list[str], arrs: list[list], max_col_len: int,
        correctness: list[bool],
    ) -> str:
        """
        format:
        | i | caption[0] | caption[1] | ... | caption[N] | Correct |
        +---+------------+------------+-----+------------+---------+
        | 0 | arrs[0][0] | arrs[1][0] | ... | arrs[N][0] |    X    |
        | 1 | arrs[0][1] | arrs[1][1] | ... | arrs[N][1] |    V    |
        ....
        +---+------------+------------+-----+------------+---------+
        """
        ret = ""
        cols = ["i"]
        cols_lens = [max(len(cols[0]), len(str(len(correctness))))]
        cols += caption
        cols_lens += [max(max_col_len, len(col)) for col in cols[1:]]
        cols.append("Correct")
        correct_s, fail_s = "V", "X"
        cols_lens.append(max(map(len, (correct_s, fail_s, cols[-1]))))
        # cols_lens[:] = (col_len + 2 for col_len in cols_lens)
        ret += "| " + " | ".join(
                col.center(col_len)
                for col, col_len in zip(cols, cols_lens)
            ) + " |\n"
        separator = "+" + "+".join("-" * (col_len + 2) for col_len in cols_lens) + "+\n"
        ret += separator
        corr_iter = (correct_s if c else fail_s for c in correctness)
        for vals in zip(range(len(correctness)), *arrs, corr_iter):
            ret += "| " + " | ".join(
                self._align_value(col, col_len)
                for col, col_len in zip(vals, cols_lens)
            ) + " |\n"
        ret += separator
        return ret

    def _align_value(self, value, max_len: int) -> str:
        if self._array_align == "center":
            return str(value).center(max_len)
        elif self._array_align == "left":
            v = str(value)
            return v + max(max_len - len(v), 0) * " "
        elif self._array_align == "right":
            v = str(value)
            return max(max_len - len(v), 0) * " " + v
        else:
            return str(value)
