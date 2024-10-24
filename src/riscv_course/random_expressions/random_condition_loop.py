import argparse
import random

LOGICAL_OPERATORS = [ '<', '<=', '>=', '>' ]
MATH_OPERATORS = [ '+', '-', '&', '|', '^' ]

THRESHOLD_RANGE = (1, 1000)
THEN_NUMBER_RANGE = (1, 100)
ELSE_NUMBER_RANGE = (1, 100)

class Task:
    def __init__(self, array_length, condition_length, seed):
        random.seed(seed)
        self.array_length = array_length
        self.threshold = random.randint(*THRESHOLD_RANGE)

        condition_indexes   = random.choices(range(array_length), k=condition_length)
        condition_operators = random.choices(MATH_OPERATORS, k=condition_length-1)
        condition_operator  = random.choice(LOGICAL_OPERATORS)

        self.then_number   = random.randint(*THEN_NUMBER_RANGE)
        self.else_number   = random.randint(*ELSE_NUMBER_RANGE)
        then_opetaror = random.choice(MATH_OPERATORS)
        else_opetaror = random.choice(MATH_OPERATORS)

        condition_string = ""
        for i in range(condition_length - 1):
            condition_string += f"arr[{condition_indexes[i]}] {condition_operators[i]} "
        condition_string += f"arr[{condition_indexes[condition_length - 1]}]"

        self.text = f"ЕСЛИ (({condition_string}) {condition_operator} {self.threshold})\n" \
            f"ТО (arr[i] = arr[i - 1] {then_opetaror} {self.then_number})\n" \
            f"ИНАЧЕ (arr[i] = arr[i] {else_opetaror} {self.else_number})"

        self.code = (
            "for i in range(len(arr)):\n"
            "\tprev = arr[i - 1] if (i - 1 >= 0) else 0\n"
           f"\tif ({condition_string}) {condition_operator} threshold:\n"
           f"\t\tarr[i] = prev {then_opetaror} then_number\n"
            "\telse:\n"
           f"\t\tarr[i] = arr[i] {else_opetaror} else_number\n")

def get_args():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument("--seed",  "-s",
                        type=int,
                        help="seed for pseudo-randomness")
    parser.add_argument("--array-length", "-l",
                        type=int,
                        help="length of array")
    parser.add_argument("--condition-length", "-c",
                        type=int,
                        help="length of condition inside the if statement")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    task = Task(args.array_length, args.condition_length, args.seed)
    print(task.text)
