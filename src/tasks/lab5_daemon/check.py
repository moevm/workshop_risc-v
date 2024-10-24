import argparse
import sys
import subprocess
import random
import init
from dataclasses import dataclass

sys.path.append('../../')

COMPILER = "riscv64-unknown-linux-gnu-g++"
DEFAULT_N_TESTS = 30
DEFAULT_N_STATES_PER_TEST =  5

@dataclass
class TestCase:
    input_buttons: int
    expected_leds: int

def compile_code(compiler, files_and_flags, output):
    p = subprocess.run(
        [compiler, *files_and_flags, "-o", output, "-static"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False
    )

    if p.returncode != 0:
        print("Failed to compile:")
        print(p.stderr.decode())
        return False
    return True

# this thing is really messy. WIP, i guess
def generate_tests(exprs, seed):
    random.seed(seed)
    tests = []

    good_exprs = []
    for expr in exprs:
        #expr = expr.replace("!", " not ")
        for i in range(init.DEFAULT_N_INPUTS):
            expr = expr.replace(f"X{i}", f"buttons[{i}]")
        good_exprs.append(expr)

    code = ""
    for i, expr in enumerate(good_exprs):
        code += f"leds[{i}] = {expr}\n"

    compiled_object = compile(code, "<string>", "exec")

    for _ in range(DEFAULT_N_TESTS):
        test = []
        for __ in range(DEFAULT_N_STATES_PER_TEST):
            buttons_num = random.randrange(0, 2**init.DEFAULT_N_INPUTS)
            buttons = []
            for i in range(init.DEFAULT_N_INPUTS):
                buttons.append((buttons_num >> i) & 1)
            leds = [0] * init.DEFAULT_N_LEDS
            exec(compiled_object)
            expected_leds = 0
            for i in range(init.DEFAULT_N_LEDS):
                expected_leds = expected_leds | ((1 if leds[i] else 0) << i)

            test.append(TestCase(buttons_num, expected_leds))
        tests.append(test)
    return tests

def run_prog(input_str, timeout):
    try:
        p = subprocess.run(["qemu-riscv64", "prog.x"], input=input_str.encode(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        res = p.stdout.decode(errors="ignore")
        if len(res) != 0:
            return res
        return None
    except subprocess.TimeoutExpired:
        return "error: timeout"
    
def run_tests(tests, timeout):
    for test in tests:
        input_str = f"{len(test)}\n"
        for state in test:
            input_str += f"{state.input_buttons} {state.expected_leds}\n"
        
        msg = run_prog(input_str, timeout)
        if msg is not None:
            print(msg)
            return 1

    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--interactive', action=argparse.BooleanOptionalAction)
    parser.add_argument('-x', type=float, required=True)
    args = parser.parse_args()

    exprs = init.generate_task(args.seed)
    compile_args = [
        "solution.s", "led.cpp",
        f"-DTIME_MULTIPLIER={args.x}"
    ]
    if not compile_code(COMPILER, compile_args, "prog.x"):
        return 1
    
    if args.interactive:
        import os
        return os.system("qemu-riscv64 prog.x interactive") & 255
    
    tests = generate_tests(exprs, args.seed)
    return run_tests(tests, args.x * 2)

if __name__ == '__main__':
    sys.exit(main())
