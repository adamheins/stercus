#!/usr/bin/env python

import argparse
import re
import sys

# Size of data available to the program (in bytes).
DATA_SIZE = 10000

# Brackets.
APPLICATOR_START = '['
APPLICATOR_END = ']'
CONDITIONAL_START = '('
CONDITIONAL_END = ')'

# Comments.
SINGLE_LINE_COMMENT_DELIMITER = '#'
MULTI_LINE_COMMENT_DELIMITER = '##'

# Built-in applications.
INCREMENT = '+'
DECREMENT = '-'
OUTPUT = '.'
INPUT = ','
NOP = '_'

class AddressOutOfRangeError(Exception):
    """ Raised when the program attempted to access an address outside the range
        of STERCUS_DATA_SIZE. """
    pass

class UnbalancedBracketsError(Exception):
    """ Raised when the program has an unbalanced number of brackets. """
    pass


def preprocess(src_file):
    """ Preprocessing step """

    def remove_comments(src):
        """ Remove multiline and single line comments from the source code. """
        MULTI_LINE_COMMENT_RULE = re.compile(MULTI_LINE_COMMENT_DELIMITER
                + '.*?' + MULTI_LINE_COMMENT_DELIMITER, re.M | re.S)
        SINGLE_LINE_COMMENT_RULE = re.compile(SINGLE_LINE_COMMENT_DELIMITER
                + '.*?$', re.M)

        src = re.sub(MULTI_LINE_COMMENT_RULE, '', src)
        src = re.sub(SINGLE_LINE_COMMENT_RULE, '', src)
        return src

    def check_bracket_balance(src):
        """ Check to ensure that brackets are correctly balanced in the source
            code. """
        applicator_count = 0
        conditional_count = 0
        prev_open = ''
        for c in src:
            if c == APPLICATOR_START:
                prev_open = APPLICATOR_START
                applicator_count += 1
            elif c == APPLICATOR_END:
                if prev_open == CONDITIONAL_START:
                    raise UnbalancedBracketsError('Mismatched brackets.')
                prev_open = ''
                applicator_count -= 1
            elif c == CONDITIONAL_START:
                prev_open = CONDITIONAL_START
                conditional_count += 1
            elif c == CONDITIONAL_END:
                if prev_open == APPLICATOR_START:
                    raise UnbalancedBracketsError('Mismatched brackets.')
                prev_open = ''
                conditional_count -= 1

            # Net bracket count must not be below 0 for either bracket type at
            # any time.
            if applicator_count < 0:
                raise UnbalancedBracketsError('Applicator brackets are not '
                        'balanced.')
            if conditional_count < 0:
                raise UnbalancedBracketsError('Conditional brackets are not '
                        'balanced.')

        # Final net count of each bracket type must be 0.
        if applicator_count != 0:
            raise UnbalancedBracketsError('Applicator brackets are not '
                    'balanced.')
        if conditional_count != 0:
            raise UnbalancedBracketsError('Conditional brackets are not '
                    'balanced.')


    # Preprocessing rules.
    PREPROCESS_RULES = {
            ' [ ': re.compile('(\s*)\[(\s*)'),
            ' ] ': re.compile('(\s*)\](\s*)'),
            ' ( ': re.compile('(\s*)\((\s*)'),
            ' ) ': re.compile('(\s*)\)(\s*)'),
    }

    with open(src_file, 'r') as f:
        src = f.read()

    src = remove_comments(src)

    check_bracket_balance(src)

    # Add space between all tokens.
    for key, val in PREPROCESS_RULES.iteritems():
        src = re.sub(val, key, src)

    # Substitute all whitespace sequences for a single space, then tokenize
    # the source.
    return re.sub(r'\s+', ' ', src).strip().split(' ')


def run(tokens):
    """ Run the program. """


    # The memory we are working with.
    data = [0] * (DATA_SIZE + 1)

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

    def accessor_is_nop(accessor):
        return accessor == DATA_SIZE

    def accessor_nop():
        return DATA_SIZE

    def get_accessor(tokens, index):
        accessor, index = expression(tokens, index)
        if accessor == NOP:
            accessor = accessor_nop()
        else:
            accessor = int(accessor)
            if accessor >= DATA_SIZE:
                raise AddressOutOfRangeError('Attempted to access address '
                        'larger than STERCUS_DATA_SIZE')
        return accessor, index

    def expression(tokens, start):
        token = tokens[start]
        if token == APPLICATOR_START:
            return applicator(tokens, start + 1)
        if token == CONDITIONAL_START:
            return conditional(tokens, start + 1)
        return token, start + 1

    def applicator(tokens, start):
        """ Parse an applicator block. """
        accessor, index = get_accessor(tokens, start)

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
        accessor, index = get_accessor(tokens, start)

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

