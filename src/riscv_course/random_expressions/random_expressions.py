import argparse
from random import choice, seed, random


def is_brackets_balanced(text, brackets="()"):
    opening, closing = brackets[::2], brackets[1::2]
    stack = []
    for character in text:
        if character in opening:
            stack.append(opening.index(character))
        elif character in closing:
            if stack and stack[-1] == closing.index(character):
                stack.pop()
            else:
                return False
    return len(stack) == 0


def is_valid_expression(expression, vars):
    try:
        safe_vars = {var: 1 for var in vars}
        eval(expression, {"__builtins__": None}, safe_vars)
        return True
    except:
        return False


def get_args():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument("--random_seed",  "-s",
                        type=str, default=None,
                        help="random seed for generation expression")

    parser.add_argument("--operations", "-O",
                        type=str, default="+",
                        help='a list of operations that can be included in an expression. Format: "op1,op2"')

    parser.add_argument("--variables", "-v",
                        type=str, default="x",
                        help='a list of variables that can be included in an expression. Format: "x,y,z,w"')

    parser.add_argument("--len", "-l",
                        type=int, default=1,
                        help="the length of the expression (operations count in expression)")

    parser.add_argument("--brackets", "-b",
                        type=float, default=False,
                        help="add brackets in the expression (The frequency is set in the range from 0 to 1)"
                        )

    parser.add_argument("--minuses", "-m",
                        type=float, default=0,
                        help="add minuses before vars [for ex.: (-x)] in the expression (The frequency is set in the range from 0 to 1)"
                        )

    parser.add_argument("--output", "-o",
                        type=str, default=0,
                        help="the output file name (if flag used, else print expression in stdout)")

    return parser.parse_args()


def get_bracket(brackets_treshold, is_open=True):
    if is_open:
        return "(" if random() < brackets_treshold else ""

    return ")" if random() < brackets_treshold else ""

def get_var(cur_vars, vars, minus_symbol, minuses_threshold, all_variables):
    need_minus = random() < minuses_threshold
    var = choice(cur_vars)
    
    if all_variables:
        cur_vars.remove(var)
        if len(cur_vars) == 0:
            cur_vars = vars.copy()

    return f"{f'({minus_symbol}{var})' if need_minus else var}"


def get_expression(
        vars, operations, length, random_seed, minuses_threshold=0,
        brackets_treshold=0, minus_symbol = "-", all_variables = False
    ):
    seed(random_seed)
    cur_vars = vars.copy()

    for _ in range(3):
        expression = ""
        stack = 0

        bracket = get_bracket(brackets_treshold)
        expression += bracket
        stack += (bracket != "")

        expression += get_var(cur_vars, vars, minus_symbol, minuses_threshold, all_variables)
        
        for i in range(length):
            expression += f" {choice(operations)} "

            if i != length - 1:
                bracket = get_bracket(brackets_treshold)
                expression += bracket
                stack += (bracket != "")

            expression += get_var(cur_vars, vars, minus_symbol, minuses_threshold, all_variables)
        
            if bracket == "":
                cur_stack = stack
                for _ in range(cur_stack):
                    bracket = get_bracket(brackets_treshold, is_open=False)
                    expression += bracket
                    stack -= (bracket != "")

        if stack > 0:
            expression += ")"*stack

        if is_brackets_balanced(expression):
            return expression

    raise ValueError("Can't genetarte expression")


def main():
    args = get_args()
    expression = get_expression(args.variables.split(","),
                                args.operations.split(","),
                                args.len,
                                args.random_seed,
                                minuses_treshold=args.minuses,
                                brackets_treshold=args.brackets)
    if args.output:
        with open(args.output, "w") as f:
            f.write(expression)
    else:
        print(expression)


if __name__ == "__main__":
    main()
