#!/usr/bin/env python

import argparse
import re
import sys


def preprocess(src_file):
    """ Preprocessing step """

    # Preprocessing rules.
    PREPROCESS_RULES = {
            ' [ ': re.compile('(\s*)\[(\s*)'),
            ' ] ': re.compile('(\s*)\](\s*)'),
            ' ( ': re.compile('(\s*)\((\s*)'),
            ' ) ': re.compile('(\s*)\)(\s*)'),
    }
    MULTI_LINE_COMMENT_RULE = re.compile('##.*?##', re.M | re.S)
    SINGLE_LINE_COMMENT_RULE = re.compile('#.*?$', re.M)

    with open(src_file, 'r') as f:
        src = f.read()

    # Strip comments.
    src = re.sub(MULTI_LINE_COMMENT_RULE, '', src)
    src = re.sub(SINGLE_LINE_COMMENT_RULE, '', src)

    # Add space between all tokens.
    for key, val in PREPROCESS_RULES.iteritems():
        src = re.sub(val, key, src)

    # Substitute all whitespace sequences for a single space, then tokenize
    # the source.
    return re.sub(r'\s+', ' ', src).strip().split(' ')


def run(tokens):
    """ Run the program. """

    APPLICATOR_START = '['
    APPLICATOR_END = ']'
    CONDITIONAL_START = '('
    CONDITIONAL_END = ')'

    # Built-in applications.
    INCREMENT = '+'
    DECREMENT = '-'
    OUTPUT = '.'
    INPUT = ','
    NOP = '_'

    # The memory we are working with.
    data = [0] * 10000

    def apply(value, accessor):
        if value == NOP:
            pass
        elif value == INCREMENT:
            data[accessor] += 1
        elif value == DECREMENT:
            data[accessor] -= 1
        elif value == OUTPUT:
            print data[accessor]
        elif value == INPUT:
            data[accessor] = ord(sys.stdin.read(1))
        else:
            return False
        return True


    def expression(tokens, start):
        if tokens[start] == APPLICATOR_START:
            return applicator(tokens, start + 1)
        if tokens[start] == CONDITIONAL_START:
            return conditional(tokens, start + 1)
        return tokens[start], start + 1

    def applicator(tokens, start):
        """ Parse an applicator block. """
        accessor, index = expression(tokens, start)
        accessor = int(accessor)

        while index < len(tokens):
            value, index = expression(tokens, index)
            if (apply(value, accessor)):
                continue
            elif value == APPLICATOR_END:
                return data[accessor], index
            else:
                data[accessor] = int(value)
        print 'Error!'

    def conditional(tokens, start):
        """ Parse a conditional block. """
        accessor, index = expression(tokens, start)
        accessor = int(accessor)

        loop_start = index
        while data[accessor] != 0:
            while index < len(tokens):
                value, index = expression(tokens, index)
                if (apply(value, accessor)):
                    continue
                elif value == CONDITIONAL_END:
                    break
                else:
                    data[accessor] = int(value)
            loop_end = index
            index = loop_start # Reset the loop
        return NOP, loop_end

    # Start the party.
    index = 0
    while (index < len(tokens)):
        _, index = expression(tokens, index)

def compile(self, out):
    pass

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='Stercus source file.')
    args = parser.parse_args()

    tokens = preprocess(args.src)
    if len(tokens) > 0:
        run(tokens)

if __name__ == '__main__':
    main()

