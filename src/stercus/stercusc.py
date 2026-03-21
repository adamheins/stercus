#!/usr/bin/env python
import argparse
from pathlib import Path
import subprocess
import tempfile

from stercus import compile_file, IndexOutOfRangeError


def main():
    parser = argparse.ArgumentParser(description="Compile Stercus to C.")
    parser.add_argument("src", help="Stercus source file.")
    parser.add_argument("-o", "--output", help="Output file for C code.")
    parser.add_argument(
        "-m",
        "--memory-size",
        type=int,
        default=10000,
        help="Number of bytes to use for program memory.",
    )
    parser.add_argument(
        "-c",
        "--c-compiler-command",
        type=str,
        help="Command to call to compile code to C. If provided, a binary is produced using this C compiler. Otherwise, the output is a C source code file.",
    )
    args = parser.parse_args()

    try:
        c_str = compile_file(args.src, memory_size=args.memory_size)
    except IndexOutOfRangeError as e:
        print(e)
        return 1

    output = args.output
    if output is None:
        output = Path(args.src).stem

    if args.c_compiler_command is None:
        with open(output + ".c", "w") as f:
            f.write(c_str)
    else:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".c", delete_on_close=False
        ) as f:
            f.write(c_str)
            f.close()

            args = [args.c_compiler_command, "-o", output, f.name]
            subprocess.run(args)


if __name__ == "__main__":
    main()
