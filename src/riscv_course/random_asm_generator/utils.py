from random import choice, seed, randint, shuffle
from math import ceil

MODE_GENERATE = "generate"
MODE_VALIDATE = "validate"

START = """.globl _start
.text
_start:

"""

END = """

\taddi a0, x0, 0
\taddi a7, x0, 93
\tecall
"""

PRINT_RESULT = "\tcall print_result\n"

REGISTERS = ["a0", "a1", "a2", "a3"]
MIN_VAL = 2
MAX_VAL = 1000

INIT_REGISTER = "addi {}, x0, {}"

IMMIDIATE_COMMANDS = ["addi", "ori", "xori" , "andi"]

REGISTER_COMMANDS = ["add", "sub", "or"]

ZEROING_COMMANDS = ["addi a0, x0, 0", "xori a0, x0, 0", "andi a0, a0, 0", "ori a0, x0, 0"]

def generate_registers_init_sequence():
    source = ""

    for r in REGISTERS:
        source += f"\t{INIT_REGISTER.format(r, randint(MIN_VAL, MAX_VAL))}\n"

    return source 

def generate_plain_line(immidiate = True):
    r1 = choice(REGISTERS)
    registers = REGISTERS
    if immidiate:
        r3 = randint(MIN_VAL, MAX_VAL)
        command = choice(IMMIDIATE_COMMANDS)
    else:
        # Random is on register command
        r3 = choice([x for x in REGISTERS if x != r1])
        command = choice(REGISTER_COMMANDS)
        registers.append("x0")
      
    r2 = choice([x for x in registers if x not in [r1, r3]])

    return f"\t{command} {r1}, {r2}, {r3}"


def generate_plain_source(length):
    immidiate_commands_length = int ( length / 2 ) 
    register_commands_length = length - immidiate_commands_length + randint(0, ceil(length/2))
    immidiate_commands_length += randint(0, ceil(length/2))

    lines = []
     
    for _ in range(immidiate_commands_length):
        lines.append(generate_plain_line())

    for _ in range(register_commands_length):
        lines.append(generate_plain_line(False))
   
    shuffle(lines)
    return "\n".join(lines) 
 

def generate_zeroing_command():
    return f"\n\t{choice(ZEROING_COMMANDS)}\n"

def generate_random_source_simple(starting_section_length, ending_section_length, mode, random_seed):
    
    # Init seed
    seed(random_seed)

    source = START + generate_registers_init_sequence() + generate_plain_source(starting_section_length)

    if mode == MODE_GENERATE:
        source += generate_zeroing_command()
        source += generate_plain_source(ending_section_length)
    elif mode == MODE_VALIDATE:
        source += f"\n{PRINT_RESULT}"
    else:
        raise ValueError(f"mode is {mode}, but it should be  {MODE_GENERATE} or {MODE_VALIDATE}")

    return source + END
