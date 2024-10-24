import argparse
import sys
import inspect
import riscv_course


def init_task(task: riscv_course.BaseTaskClass):
    print(task.init_task())


def check_task(task: riscv_course.BaseTaskClass, solfile: str):
    task.load_student_solution(solfile)
    passed, msg = task.check()
    print("Passed:", passed)
    print(msg)
    sys.exit(0 if passed else 1)

def dry_run_task(task: riscv_course.BaseTaskClass):
    task.generate_task()
    task._generate_tests()
    for i, test in enumerate(task.tests):
        print(f"TEST #{i+1}:\n\t{test}")
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    for _, cli_parser in inspect.getmembers(riscv_course, lambda obj: isinstance(obj, riscv_course.CLIParser)):
        task_parser = subparsers.add_parser(cli_parser.name)
        cli_parser.add_cli_args(task_parser)

    args = parser.parse_args()
    task = args.func(args)

    match args.mode:
        case "init": init_task(task)
        case "check": check_task(task, args.solution)
        case "dry-run": dry_run_task(task)
