#!/usr/bin/env python

# Converts an ascii string into the equivalent expression for output in
# stercus.

import argparse

def parse(text):
    stercus = ''
    for char in text:
        stercus += str(ord(char)) + ' . '
    return stercus

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('text')
    args = parser.parse_args()
    print parse(args.text)

if __name__ == '__main__':
    main()

