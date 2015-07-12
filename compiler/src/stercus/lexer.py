#!/usr/bin/env python
""" Stercus Language Lexer """

import argparse

from constants import BRACKETS

def lex(src):
    """ Convert the Stercus source code into a list of tokens. """
    lexed_src = ''
    for char in src:
        if char in BRACKETS['ALL']:
            lexed_src += ' ' + char + ' '
        else:
            lexed_src += char
    return lexed_src.split()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='Stercus source file.')
    parser.add_argument('-o', '--output', help='Output file for lexed tokens',
                        dest='out')
    args = parser.parse_args()

    with open(args.src, 'r') as f:
        src = f.read()

    # Output the result.
    tokens = lex(src)
    if args.out:
        with open(args.out, 'w') as f:
            f.write(' '.join(tokens))
    else:
        print ' '.join(tokens)

if __name__ == '__main__':
    main()
