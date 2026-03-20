"""Converts an ascii string into the equivalent expression for output in stercus."""

import argparse


def parse(text):
    code = " : ".join([str(ord(char)) for char in text])
    return f"[0 {code}]"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    args = parser.parse_args()
    print(parse(args.text))


if __name__ == "__main__":
    main()
