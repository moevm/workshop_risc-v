import argparse
from riscv_course.base_module.base_cli import CLIParser, add_common_cli_args, get_common_cli_args
from .lab5_daemon import Lab5Daemon

DEFAULT_TIME_SCALE = 3
DEFAULT_N_LEDS = 8
DEFAULT_N_BUTTONS = 8

def create_task_lab5(args) -> Lab5Daemon:
    task = Lab5Daemon(
        interactive=args.interactive,
        time_scale=args.time_scale,
        n_leds=args.leds,
        n_buttons=args.buttons,
        # Common args
        **get_common_cli_args(args),
    )
    return task


def add_cli_args_lab5(parser: argparse.ArgumentParser):
    add_common_cli_args(parser)
    parser.add_argument('--interactive', '-i', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--time-scale', '-x', type=float, default=DEFAULT_TIME_SCALE)
    parser.add_argument('--leds', type=int, default=DEFAULT_N_LEDS)
    parser.add_argument('--buttons', type=int, default=DEFAULT_N_BUTTONS)
    parser.set_defaults(func=create_task_lab5)


Lab5CLIParser = CLIParser(
    name="lab5_daemon",
    add_cli_args=add_cli_args_lab5,
)
