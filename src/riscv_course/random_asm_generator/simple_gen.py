import argparse

from utils import MODE_GENERATE, generate_random_source_simple

def get_args():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("--random_seed",  "-s",
                        type=str, default=None, required=True,
                        help="random seed for code generation")

    parser.add_argument("--starting_section_length", "-H",
                        type=int, default=10,
                        help="length of starting section, lines")

    parser.add_argument("--ending_section_length", "-M",
                        type=int, default=4,
                        help="length of ending section, lines")


    parser.add_argument("--mode", "-m",
                        type=str, default=MODE_GENERATE,
                        help="script mode: generate (create binary for debugging), validate (output correct answer)")


    return parser.parse_args()

def main():
    args = get_args()
    source = generate_random_source_simple(args.starting_section_length,
                                args.ending_section_length,
                                args.mode,
                                args.random_seed)
    with open("main.s", "w") as f:
        f.write(source)
 
if __name__ == "__main__":
    main()
