#!/usr/bin/env python
""" Stercus Language Preprocessor. """

import argparse
import re
import sys

from constants import *

def remove_comments(src):
    """ Remove multiline and single line comments from the source code. """
    MULTI_LINE_COMMENT_RULE = re.compile(MULTI_LINE_COMMENT_DELIMITER
            + '.*?' + MULTI_LINE_COMMENT_DELIMITER, re.M | re.S)
    SINGLE_LINE_COMMENT_RULE = re.compile(SINGLE_LINE_COMMENT_DELIMITER
            + '.*?$', re.M)

    src = re.sub(MULTI_LINE_COMMENT_RULE, '', src)
    src = re.sub(SINGLE_LINE_COMMENT_RULE, '', src)
    return src

def preprocess(src):
    """ Preprocess the Stercus source code so that it can be lexed. """
    return remove_comments(src)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='Stercus source file.')
    parser.add_argument('-o', '--output', help='Output file for preprocessed'
                        'result.', dest='out')
    args = parser.parse_args()

    with open(args.src, 'r') as f:
        src = f.read()

    src = preprocess(src)

    # Output the result.
    if args.out:
        with open(args.out, 'w') as f:
            f.write(src)
    else:
        print src

if __name__ == '__main__':
    main()
