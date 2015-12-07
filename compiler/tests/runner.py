#!/usr/bin/env python

# Runner for all stercus unit tests.

import unittest

import parser

def main():
    result = unittest.TestResult()
    parser.suite().run(result)

if __name__ == '__main__':
    main()
