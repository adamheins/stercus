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
    def apply(application, accessor):
        if application == NOP:
            pass
        elif application == INCREMENT:
            data[accessor] += 1
        elif application == DECREMENT:
            data[accessor] -= 1
        elif application == OUTPUT:
            print data[accessor]
        elif application == INPUT:
            data[accessor] = ord(sys.stdin.read(1))
        else:
            data[accessor] = int(application)

    def push(token, index):
        try:
            value = int(token)
            if len(stack) > 0 and data[value] == 0 and stack[-1] == CONDITIONAL_START:
                stack.pop()
                while tokens[index] != CONDITIONAL_END:
                    index += 1
            else:
                stack.append(token)
        except:
            stack.append(token)
        return index

    # The memory we are working with.
    data = [0] * (DATA_SIZE + 1)

    stack = []
    loop_index_stack = []

    index = 0
    while (index < len(tokens)):
        token = tokens[index]
        if token == APPLICATOR_END:
            li = []
            val = stack.pop()
            while val != APPLICATOR_START:
                li.append(val)
                val = stack.pop()
            li.reverse()
            accessor = int(li[0])
            for application in li[1:]:
                apply(application, accessor)
            index = push(accessor, index)
        elif token == CONDITIONAL_END:
            li = []
            val = stack.pop()
            while (val != CONDITIONAL_START):
                li.append(val)
                val = stack.pop()
            accessor = int(li[-1])
            if data[accessor] != 0:
                index = loop_index_stack.pop()
                continue
        elif token == CONDITIONAL_START:
            loop_index_stack.append(index)
            stack.append(token)
        else:
            index = push(token, index)
        index += 1

def compile(tokens, out_file):
    def apply(application, accessor):
        ele = 'd[' + accessor + ']';
        if application == NOP:
            pass
        elif application == INCREMENT:
            output.append(ele + '++;')
        elif application == DECREMENT:
            output.append(ele + '--;')
        elif application == OUTPUT:
            output.append('putchar(' + ele + ');')
        elif application == INPUT:
            output.append(ele + ' = getchar();')
        else:
            output.append(ele + ' = ' + application + ';')

    output = ['#include <stdio.h>\n#include <stdlib.h>\n']
    output.append('int main() {')
    output.append('unsigned char *d = (unsigned char *)calloc('
            + str(DATA_SIZE) + ', 1);')

    stack = []

    for token in tokens:
        if token == APPLICATOR_END:
            li = []
            val = stack.pop()
            while val != APPLICATOR_START:
                li.append(val)
                val = stack.pop()
            li.reverse()
            accessor = li[0]
            for application in li[1:]:
                apply(application, accessor)
            if len(stack) > 0 and stack[-1] == CONDITIONAL_START:
                output.append('if(!d[' + accessor + ']){break;}')
            stack.append('d[' + accessor + ']')
        elif token == CONDITIONAL_END:
            val = stack.pop()
            while val != CONDITIONAL_START:
                val = stack.pop()
            output.append('}')
        elif token == CONDITIONAL_START:
            output.append('while(1){')
            stack.append(token)
        elif token == APPLICATOR_START:
            stack.append(token)
        else:
            # Check if the token is the accessor for a conditional.
            if len(stack) > 0 and stack[-1] == CONDITIONAL_START:
                output.append('if(!d[' + token + ']){break;}')
            stack.append(token)

    output.append('return 0;\n}')
    with open(out_file, 'w') as out:
        out.write('\n'.join(output))

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='Stercus source file.')
    args = parser.parse_args()

    tokens = preprocess(args.src)
    if len(tokens) > 0:
        #run(tokens)
        compile(tokens, 'out.c')

if __name__ == '__main__':
    main()

