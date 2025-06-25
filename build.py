import argparse
import sys
import inspect
import riscv_course

if __name__ == "__main__":
    for _, cli_parser in inspect.getmembers(riscv_course, lambda obj: isinstance(obj, riscv_course.CLIParser)):
        parser = argparse.ArgumentParser()
        cli_parser.add_cli_args(parser)
        args = parser.parse_args("")
        task = args.func(args)
        
        print(f"Compiling {cli_parser.name}")
        err = task.compile_static()

        if err is not None:
            print(f"Ошибка во время компиляции: {err}")
            sys.exit(1)
