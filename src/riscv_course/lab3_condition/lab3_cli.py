import argparse
from riscv_course.base_module.base_cli import CLIParser, add_common_cli_args, get_common_cli_args
from .lab3_condition import Lab3Condition, DEFAULT_MAX_LENGTH_DEVIATION, \
    CONDITION_DEFAULT_LEN, ARRAY_DEFAULT_LEN


LAB1_DEFAULT_INT_TYPE = "int64"


def create_task_lab3(args) -> Lab3Condition:
    task = Lab3Condition(
        array_length=args.array_length, condition_length=args.condition_length,
        max_length_deviation=args.max_length_deviation,
        min_value=args.min_value, max_value=args.max_value,
        # Common args
        **get_common_cli_args(args),
    )
    return task


def add_cli_args_lab3(parser: argparse.ArgumentParser):
    add_common_cli_args(parser)
    parser.add_argument('-l', '--array-length', type=int, default=ARRAY_DEFAULT_LEN)
    parser.add_argument('-c', '--condition-length', type=int, default=CONDITION_DEFAULT_LEN)
    parser.add_argument('-d', '--max-length-deviation', type=int, default=DEFAULT_MAX_LENGTH_DEVIATION)
    parser.add_argument('--min-value', type=int, default=None)
    parser.add_argument('--max-value', type=int, default=None)
    parser.set_defaults(func=create_task_lab3)


Lab3CLIParser = CLIParser(
    name="lab3_condition",
    add_cli_args=add_cli_args_lab3,
)
