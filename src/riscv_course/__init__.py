from .base_module import BaseTaskClass, CLIParser  # noqa: F401
# from .lab1_asm_intro import Lab1AsmInto, Lab1CLIParser  # noqa: F401
# from .lab3_condition import Lab3Condition, Lab3CLIParser  # noqa: F401
from .token import generate_answer_token

def __load_lab_modules():
    import importlib
    import os
    import sys
    import inspect

    cur_loc = __path__[0]

    for name in os.listdir(cur_loc):
        if name.startswith("lab") and os.path.isdir(f"{cur_loc}/{name}"):
            lab = name[:name.find("_")]
            lab = lab[0].capitalize() + lab[1:]
            mod = importlib.import_module(f".{name}", "riscv_course")
            for name, obj in inspect.getmembers(mod):
                if isinstance(obj, (BaseTaskClass, CLIParser)):
                    sys.modules[__name__].__setattr__(name, obj)


__load_lab_modules()
