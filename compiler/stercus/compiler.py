#!/usr/bin/env python
""" Stercus Language Compiler """

import argparse
import json

from constants import *

C_FUNCTION_ARG = 's0'
C_DATA_ARRAY = 'd0'

def apply(output, application, accessor, func_list):
    """ Apply an application to the accessed location. """
    ele = 'd0[' + accessor + ']';
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

def compile_body(tokens, func_list):
    output = []
    stack = []
    for token in tokens:
        if token == APPLICATOR['CLOSE']:
            li = []
            val = stack.pop()
            while val != APPLICATOR['OPEN']:
                li.append(val)
                val = stack.pop()
            li.reverse()
            accessor = li[0]
            for application in li[1:]:
                apply(output, application, accessor, func_list)
            if len(stack) > 0 and stack[-1] == CONDITIONAL['OPEN']:
                output.append('if(!d0[d0[' + accessor + ']]){break;}')
            stack.append('d0[' + accessor + ']')
        elif token == CONDITIONAL['CLOSE']:
            val = stack.pop()
            while val != CONDITIONAL['OPEN']:
                val = stack.pop()
            output.append('}')
        elif token == CONDITIONAL['OPEN']:
            output.append('while(1){')
            stack.append(token)
        elif token == APPLICATOR['OPEN']:
            stack.append(token)
        else:
            # Check if the token is the accessor for a conditional.
            if len(stack) > 0 and stack[-1] == CONDITIONAL['OPEN']:
                output.append('if(!d0[' + token + ']){break;}')
            stack.append(token)
    return '\n'.join(output)

def compile_application(name, tokens, func_list):
    """ Compile a function from stercus to C. """
    output = 'void ' + name + '(unsigned int s0) {'
    output += compile_body(tokens, func_list)
    output += '}'
    return output

def compile_main(tokens, func_list):
    """ Compile the main C function. """
    output = 'int main(void) {'
    output += 'd0=(unsigned char *)calloc(' + str(DATA_SIZE) + ', 1);'
    output += compile_body(tokens, func_list)
    output += 'free(d0);'
    output += 'return 0;}'
    return output

def compile(applications):
    """ Compile the Stercus function table to C. """

    # Save and remove the main function, as it must be placed at the end of the
    # generated C code.
    main_appl = applications['main']
    applications.pop('main')

    # Initial C boilerplate.
    c_src = '#include <stdio.h>\n#include <stdlib.h>\nunsigned char *d0;'

    # Compile applications into C functions.
    for app in applications:
        c_src += compile_application(app, applications[app],
                applications.keys())

    # Compile the main function.
    c_src += compile_main(main_appl, applications.keys())
    return c_src

def main():
    """ Run the compiler as an independent program. """
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='Stercus source file.')
    parser.add_argument('-o', '--output', help='Output file for compiled'
                        ' result.', dest='out')
    args = parser.parse_args()

    # Tokens are read from a whitespace-separated list in a file.
    with open(args.src, 'r') as f:
        applications = json.load(f)

    # Output the result.
    c_src = compile(applications)
    if args.out:
        with open(args.out, 'w') as f:
            f.write(c_src)
    else:
        print c_src

if __name__ == '__main__':
    main()
