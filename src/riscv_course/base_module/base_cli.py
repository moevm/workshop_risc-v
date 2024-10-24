import argparse
from typing import Any, Callable
from dataclasses import dataclass
from riscv_course.base_module.base_task import BaseTaskClass, DEFAULT_TEST_NUM


@dataclass
class CLIParser:
    name: str
    add_cli_args: Callable[[argparse.ArgumentParser], BaseTaskClass]


def add_common_cli_args(parser: argparse.ArgumentParser):
    parser.add_argument('-s', '--seed', type=int)
    parser.add_argument('--solution', type=str, default="solution.s")
    parser.add_argument('-n', '--n-tests', type=int, default=DEFAULT_TEST_NUM)
    parser.add_argument("-a", "--all-tests", action='store_true')
    parser.add_argument("--mode", type=str, choices=("init", "check", "dry-run"), default="init")
    parser.add_argument("--array-align", type=str, choices=("center", "left", "right"), default="center")
    parser.add_argument("--jail-exec", type=str, default="chroot")
    parser.add_argument("--jail-path", type=str, default=None)


def get_common_cli_args(args) -> dict[str, Any]:
    return {
        "seed": args.seed,
        "tests_num": args.n_tests,
        "fail_on_first_test": not args.all_tests,
        "array_align": args.array_align,
        "jail_exec": args.jail_exec,
        "jail_path": args.jail_path,
    }
