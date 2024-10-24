import argparse
from riscv_course.base_module.base_cli import CLIParser, add_common_cli_args, get_common_cli_args
from .lab2_debug import Lab2Debug, DEFAULT_START_SECTION_LEN, \
    DEFAULT_END_SECTION_LEN


def create_task_lab2(args) -> Lab2Debug:
    task = Lab2Debug(
        starting_section_length=args.starting_section_length,
        ending_section_length=args.ending_section_length,
        answer=args.answer, interactive=args.interactive_init,
        print_task_when_i=args.print_task_when_interactive,
        # Common args
        **get_common_cli_args(args),
    )
    return task


def add_cli_args_lab2(parser: argparse.ArgumentParser):
    add_common_cli_args(parser)
    parser.add_argument("--starting-section-length", type=int, default=DEFAULT_START_SECTION_LEN)
    parser.add_argument("--ending-section-length", type=int, default=DEFAULT_END_SECTION_LEN)
    parser.add_argument("--answer", type=str, default="")
    parser.add_argument("-i", "--interactive-init", action='store_true')
    parser.add_argument("--print-task-when-interactive", action='store_true')
    parser.set_defaults(func=create_task_lab2)


Lab2CLIParser = CLIParser(
    name="lab2_debug",
    add_cli_args=add_cli_args_lab2,
)
