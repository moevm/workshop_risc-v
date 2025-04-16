import argparse
from ..base_module.base_cli import CLIParser, add_common_cli_args, get_common_cli_args
from .lab8_branch import Lab8Branch, INT_TYPES


LAB2_DEFAULT_INT_TYPE = "int64"

def create_task_lab8(args) -> Lab8Branch:
    task = Lab8Branch(
        n=args.n,
        deep=args.deep,
        student_id=args.id,
        **get_common_cli_args(args),
    )
    return task

def add_cli_args_lab8(parser: argparse.ArgumentParser):
    add_common_cli_args(parser)
    # parser.add_argument('--a2', type=str, choices=INT_TYPES.keys(), default=LAB2_DEFAULT_INT_TYPE)
    # parser.add_argument('--a3', type=str, choices=INT_TYPES.keys(), default=LAB2_DEFAULT_INT_TYPE)
    # parser.add_argument('--a2-min', type=int)
    # parser.add_argument('--a2-max', type=int)
    # parser.add_argument('--a3-min', type=int)
    # parser.add_argument('--a3-max', type=int)
    parser.add_argument('--n', type=int, default=10, help="Number of functions")
    parser.add_argument('--deep', type=float, default=0.6, help="Main path depth coefficient")
    # parser.add_argument('--id', type=int, required=True, help="Student ID for variant generation")
    parser.add_argument('--id', type=int, default=238330, help="Student ID for variant generation")
    parser.set_defaults(func=create_task_lab8)

Lab8CLIParser = CLIParser(
    name="lab8_branch",
    add_cli_args=add_cli_args_lab8,
)
