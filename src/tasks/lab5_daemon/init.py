import random
import argparse
import sys

sys.path.append('../../')
import random_expressions.random_expressions as generator
#import utils.run_solution as utils

DEFAULT_N_LEDS = 8
DEFAULT_N_INPUTS = 8
DEFAULT_BINARY_OPERATIONS = ['&', '|', '^'] # AND, OR, XOR
DEFAULT_LENGTH = 2
DEFAULT_MINUSES_THRESHOLD = 0.1
DEFAULT_BRACKETS_THRESHOLD = 0.8

def generate_task(seed):
    variables = [f"X{i}" for i in range(DEFAULT_N_INPUTS)]

    exprs = []

    cur_seed = seed
    for i in range(DEFAULT_N_LEDS):
        expr = generator.get_expression(variables, DEFAULT_BINARY_OPERATIONS, DEFAULT_LENGTH, cur_seed, DEFAULT_MINUSES_THRESHOLD, DEFAULT_BRACKETS_THRESHOLD, "not ")
        exprs.append(expr)
        cur_seed = random.randint(0, 2**32)
    return exprs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()

    exprs = generate_task(args.seed)
    for i, expr in enumerate(exprs):
        print(f"Y{i} = {expr}")


if __name__ == "__main__":
    main()
