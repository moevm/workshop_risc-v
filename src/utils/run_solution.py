import subprocess
import os

# returns exit code and student`s work output
# throws subprocess.TimeoutExpired on timeout

DEFAULT_QFLAGS = ''
DEFAULT_TIMEOUT = 5

def run_solution(input: str, qflags: str = DEFAULT_QFLAGS, get_stderr = True):
    timeout = int(os.getenv('PARAM_TIMEOUT', DEFAULT_TIMEOUT))
    run = subprocess.run(f'qemu-riscv64 {qflags} prog.x', shell=True, input=input.encode(), capture_output=True, timeout=timeout)
    
    if get_stderr:
        return run.returncode, run.stderr.decode().strip()
    return run.returncode, run.stdout.decode().strip()
