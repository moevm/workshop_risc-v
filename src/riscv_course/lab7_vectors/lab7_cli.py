import argparse
from riscv_course.base_module.base_cli import CLIParser, add_common_cli_args, get_common_cli_args
from .lab7_vectors import Lab7Vectors, ARRAY_DEFAULT_LEN, DEFAULT_MAX_LENGTH_DEVIATION


def create_task_lab7(args) -> Lab7Vectors:
    task = Lab7Vectors(
        length=args.exp_length, minuses=args.minuses,
        brackets=args.brackets, operations=args.operations,
        array_length=args.array_length,
        max_length_deviation=args.max_length_deviation,
        min_value=args.min_value, max_value=args.max_value,
        # Common args
        **get_common_cli_args(args),
    )
    return task


def add_cli_args_lab7(parser: argparse.ArgumentParser):
    add_common_cli_args(parser)
    parser.add_argument('-l', '--array-length', type=int, default=ARRAY_DEFAULT_LEN)
    parser.add_argument('-d', '--max-length-deviation', type=int, default=DEFAULT_MAX_LENGTH_DEVIATION)
    parser.add_argument('--min-value', type=int, default=None)
    parser.add_argument('--max-value', type=int, default=None)
    parser.add_argument("-e", "--exp-length", type=int, default=8)
    parser.add_argument("-m", "--minuses", type=float, default=0.0)
    parser.add_argument("-b", "--brackets", type=float, default=0.5)
    parser.add_argument("-o", "--operations", type=str, default="+,-,*,&,|")
    parser.set_defaults(func=create_task_lab7)


Lab7CLIParser = CLIParser(
    name="lab7_vectors",
    add_cli_args=add_cli_args_lab7
)
