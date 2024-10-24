import argparse
from riscv_course.base_module.base_cli import CLIParser, add_common_cli_args, get_common_cli_args
from .lab4_string import Lab4String, DEFAULT_MIN_TEST_LENGTH, \
    DEFAULT_MAX_TEST_LENGTH, DEFAULT_NUM_OPERATIONS


def create_task_lab4(args) -> Lab4String:
    task = Lab4String(
        min_test_length=args.min_test_length,
        max_test_length=args.max_test_length,
        num_operations=args.num_operations,
        # Common args
        **get_common_cli_args(args),
    )
    return task


def add_cli_args_lab4(parser: argparse.ArgumentParser):
    add_common_cli_args(parser)
    parser.add_argument('-m', '--min-test-length', type=int, default=DEFAULT_MIN_TEST_LENGTH)
    parser.add_argument('-M', '--max-test-length', type=int, default=DEFAULT_MAX_TEST_LENGTH)
    parser.add_argument('-N', '--num-operations',  type=int, default=DEFAULT_NUM_OPERATIONS)
    parser.set_defaults(func=create_task_lab4)


Lab4CLIParser = CLIParser(
    name="lab4_string",
    add_cli_args=add_cli_args_lab4
)
