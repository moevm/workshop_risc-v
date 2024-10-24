import argparse
from riscv_course.base_module.base_cli import CLIParser, add_common_cli_args, get_common_cli_args
from .lab1_asm_intro import Lab1AsmInto, INT_TYPES


LAB1_DEFAULT_INT_TYPE = "int64"


def create_task_lab1(args) -> Lab1AsmInto:
    task = Lab1AsmInto(
        a2_class=args.a2, a3_class=args.a3, a4_class=args.a4,
        a2_min=args.a2_min, a2_max=args.a2_max,
        a3_min=args.a2_min, a3_max=args.a3_max,
        a4_min=args.a2_min, a4_max=args.a4_max,
        length=args.length, minuses=args.minuses, brackets=args.brackets,
        operations=args.operations,
        # Common args
        **get_common_cli_args(args),
    )
    return task


def add_cli_args_lab1(parser: argparse.ArgumentParser):
    add_common_cli_args(parser)
    parser.add_argument('--a2', type=str, choices=INT_TYPES.keys(), default=LAB1_DEFAULT_INT_TYPE)
    parser.add_argument('--a3', type=str, choices=INT_TYPES.keys(), default=LAB1_DEFAULT_INT_TYPE)
    parser.add_argument('--a4', type=str, choices=INT_TYPES.keys(), default=LAB1_DEFAULT_INT_TYPE)
    parser.add_argument('--a2-min', type=int)
    parser.add_argument('--a3-min', type=int)
    parser.add_argument('--a4-min', type=int)
    parser.add_argument('--a2-max', type=int)
    parser.add_argument('--a3-max', type=int)
    parser.add_argument('--a4-max', type=int)
    parser.add_argument("-l", "--length", type=int, default=7)
    parser.add_argument("-m", "--minuses", type=float, default=0.1)
    parser.add_argument("-b", "--brackets", type=float, default=0.8)
    parser.add_argument("-o", "--operations", type=str, default="+,-,*,&,|")
    parser.set_defaults(func=create_task_lab1)


Lab1CLIParser = CLIParser(
    name="lab1_asm_intro",
    add_cli_args=add_cli_args_lab1,
)
