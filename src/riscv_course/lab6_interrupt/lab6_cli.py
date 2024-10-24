import argparse
from riscv_course.base_module.base_cli import CLIParser, add_common_cli_args, get_common_cli_args
from .lab6_interrupt import Lab6Interrupt
import riscv_course.int_utils as int_utils

def create_task_lab6(args) -> Lab6Interrupt:
    task = Lab6Interrupt(
        args.a_type, args.b_type, args.c_type, args.result_type,
        args.a_min, args.a_max,
        args.b_min, args.b_max,
        args.c_min, args.c_max,
        # Common args
        **get_common_cli_args(args),
    )
    return task


def add_cli_args_lab6(parser: argparse.ArgumentParser):
    add_common_cli_args(parser)
    parser.add_argument('--a-type', type=str, default="int64", choices=int_utils.INT_TYPES.keys())
    parser.add_argument('--b-type', type=str, default="int64", choices=int_utils.INT_TYPES.keys())
    parser.add_argument('--c-type', type=str, default="int64", choices=int_utils.INT_TYPES.keys())
    parser.add_argument('--result-type', type=str, default="int64", choices=int_utils.INT_TYPES.keys())
    parser.add_argument('--a-min', type=int, default=None)
    parser.add_argument('--a-max', type=int, default=None)
    parser.add_argument('--b-min', type=int, default=None)
    parser.add_argument('--b-max', type=int, default=None)
    parser.add_argument('--c-min', type=int, default=None)
    parser.add_argument('--c-max', type=int, default=None)
    parser.set_defaults(func=create_task_lab6)


Lab6CLIParser = CLIParser(
    name="lab6_interrupt",
    add_cli_args=add_cli_args_lab6,
)
