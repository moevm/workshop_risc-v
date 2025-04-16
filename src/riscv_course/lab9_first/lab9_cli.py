import argparse
from ..base_module.base_cli import CLIParser, add_common_cli_args, get_common_cli_args
from .lab9_first import Lab9First, INT_TYPES


LAB9_DEFAULT_INT_TYPE = "int64"

def create_task_lab9(args) -> Lab9First:
    task = Lab9First(
        n=args.n,
        deep=args.deep,
        student_id=args.id,
        **get_common_cli_args(args),
    )
    return task

def add_cli_args_lab9(parser: argparse.ArgumentParser):
    add_common_cli_args(parser)
    parser.add_argument('--n', type=int, default=10, help="Number of functions")
    parser.add_argument('--deep', type=float, default=6, help="Main path depth coefficient")
    parser.add_argument('--id', type=int, default=238330, help="Student ID for variant generation")
    parser.set_defaults(func=create_task_lab9)

Lab9CLIParser = CLIParser(
    name="lab9_first",
    add_cli_args=add_cli_args_lab9,
)
