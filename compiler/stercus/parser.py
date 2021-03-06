#!/usr/bin/env python
""" Stercus Language Parser """

import argparse
import json
from string import ascii_letters

from constants import *
from errors import *


def check_brackets(tokens):
    counts = {
        '(': 0,
        '[': 0,
        '{': 0,
    }
    openings = []
    for token in tokens:
        if token in BRACKETS['OPEN']:
            openings.append(token)

            # Applications must not be nested within any expressions.
            if token == '{':
                for _, count in counts.items():
                    if count > 0:
                        raise UnbalancedBracketsError('Application definitions'
                                ' must not be nested within any expressions.')
            counts[token] += 1
        elif token in BRACKETS['CLOSE']:

            # If the stack ever empties and a closing bracket is encounted,
            # the brackets must be unbalanced.
            try:
                opening = openings.pop()
            except IndexError:
                raise UnbalancedBracketsError('Too many closing brackets of'
                        ' type "' + token + '".')

            # The opening and closing brackets must match.
            if BRACKETS['PAIRS'][opening] != token:
                raise UnbalancedBracketsError('Opening and closing brackets do'
                        ' not match.')
            counts[opening] -= 1

def check_application_name(name):
    """ Check if the application name is valid. """
    # Application names may only contain letters and underscores.
    for char in name:
        if char not in ascii_letters and char != '_':
            raise ApplicationNameError('Invalid application name: ' + name
                    + '. Application names may only contain letters.')

def parse_applications(tokens):
    """ Parse the applications in the program. """
    applications = {}
    open_index = 0
    index = 0
    while index < len(tokens):
        if tokens[index] == APPLICATION['OPEN']:
            open_index = index
        elif tokens[index] == APPLICATION['CLOSE']:
            # Check the application name.
            app_name = tokens[open_index + 1]
            check_application_name(app_name)

            # Add the application to the application table.
            applications[app_name] = tokens[open_index + 2:index]

            # Remove the application body from the tokens.
            tokens = tokens[:open_index] + tokens[index + 1:]
            index = open_index
            continue
        index += 1
    applications['main'] = tokens
    return applications

def parse(tokens):
    """ Parse the Stercus tokens into separate applications. """
    check_brackets(tokens)
    # Replace the '$' because that is not a valid variable name in C.
    tokens = ['s0' if token == '$' else token for token in tokens]
    for token in tokens:
        if token == 'main':
            raise ApplicationNameError("Application named 'main' is not"
                                       " allowed.")
    return parse_applications(tokens)

def main():
    """ Run the parser as an independent program. """
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='Stercus source file.')
    parser.add_argument('-o', '--output', help='Output file for parsed result.',
                        dest='out')
    args = parser.parse_args()

    # Tokens are read from a whitespace-separated list in a file.
    with open(args.src, 'r') as f:
        tokens = f.read().split()

    # Output the result.
    applications = parse(tokens)
    if args.out:
        with open(args.out, 'w') as f:
            json.dump(applications, f)
    else:
        print applications

if __name__ == '__main__':
    main()
