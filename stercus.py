#!/usr/bin/env python

import argparse
import re
import sys
from subprocess import call

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

class FunctionNameError(Exception):
    """ Raised when a disallowed function name is encountered. """
    pass


def preprocess(src):
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

    def tokenize(src):
        """ Convert the source string to a list of tokens. """
        processed_src = ''
        for char in src:
            if char in '[](){}':
                processed_src += ' ' + char + ' '
            elif char == '$':
                processed_src += '_s'
            else:
                processed_src += char
        return processed_src.split()

    def check_func_name(name):
        """ Check if the function name is valid. """
        if not name.isalpha():
            raise FunctionNameError('Unacceptable function name: ' + name
                    + '. Function names may only contain letters.')
        return name

    def parse_functions(tokens):
        """ Parse the functions in the program. """
        functions = {}
        open_index = 0
        index = 0
        while index < len(tokens):
            if tokens[index]== '{':
                open_index = index
            elif tokens[index] == '}':
                # Check the function name.
                func_name = tokens[open_index + 1]
                check_func_name(func_name)

                # Add the function to the function table.
                functions[func_name] = tokens[open_index + 2 : index]

                # Remove the function body from the tokens.
                tokens = tokens[:open_index] + tokens[index + 1:]
                index = open_index
                continue
            index += 1
        return tokens, functions

    src = remove_comments(src)
    check_bracket_balance(src)
    tokens = tokenize(src)
    tokens, functions = parse_functions(tokens)

    return tokens, functions

def compile_function(name, args, tokens, func_list):
    """ Compile a function from stercus to C. """

    def apply(application, accessor):
        """ Apply an application to the accessed location. """
        ele = '_d[' + accessor + ']';
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
        elif application in func_list:
            output.append(application + '(' + accessor + ');')
        else:
            output.append(ele + ' = ' + application + ';')

    output = ['void ' + name + '(' + args + ') {']
    if name == 'main':
        output.append('_d=(unsigned char *)calloc(' + str(DATA_SIZE) + ', 1);')
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
                output.append('if(!_d[_d[' + accessor + ']]){break;}')
            stack.append('_d[' + accessor + ']')
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
                output.append('if(!_d[' + token + ']){break;}')
            stack.append(token)

    output.append('}')
    return '\n'.join(output)

def main():
    """ Main entry point for stercus compilation. """

    # Parse command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='Stercus source file.')
    parser.add_argument('-c', '--compile', help='Compile the stercus file to C,'
                        ' rather than interpreting it.', dest='compile',
                        action='store_true')
    parser.add_argument('--gcc', help='Compile directly to native code using'
                        ' GCC.', dest='gcc', action='store_true')
    parser.add_argument('-o', '--output', help='C file to which to output'
                        ' compiled stercus.', dest='out')
    args = parser.parse_args()

    # Read the source file.
    with open(args.src, 'r') as f:
        src = f.read()

    # Process the source code to extract functions and script parts.
    script, functions = preprocess(src)

    # C boilerplate.
    c = '#include <stdio.h>\n#include <stdlib.h>\nunsigned char *_d;'

    func_list = functions.keys()

    # Compile each function.
    for func in functions:
        c += compile_function(func, 'unsigned int _s', functions[func], func_list)

    # Compile the main function last.
    c += compile_function('main', 'void', script, func_list)

    # Write the C code out to a file.
    if args.out:
        out_file = args.out
    else:
        out_file = 'out.c'
    with open(out_file, 'w') as f:
        f.write(c)
    if args.gcc:
        call(['gcc', out_file])
        call(['rm', out_file])

if __name__ == '__main__':
    main()

