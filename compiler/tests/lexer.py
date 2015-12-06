#!/usr/bin/env python

import os
import sys
import unittest

# Allow stercus module to be imported.
CUR_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CUR_DIR, os.pardir))
sys.path.insert(0, ROOT_DIR)

from stercus import lexer

class LexerTest(unittest.TestCase):
    def test_lex_applicator(self):
        program = '[0 , .]'
        expected = ['[', '0', ',', '.', ']']
        actual = lexer.lex(program)
        self.assertListEqual(actual, expected)

    def test_lex_conditional(self):
        program = '(0 [0 -])'
        expected = ['(', '0', '[', '0', '-', ']', ')']
        actual = lexer.lex(program)
        self.assertListEqual(actual, expected)

    def test_lex_newline(self):
        program = '[0\n,]'
        expected = ['[', '0', ',', ']']
        actual = lexer.lex(program)
        self.assertListEqual(actual, expected)

    def test_lex_large_numbers(self):
        program = '[10\n934]'
        expected = ['[', '10', '934', ']']
        actual = lexer.lex(program)
        self.assertListEqual(actual, expected)

    def test_lex_big_whitespace(self):
        program = '[\t0       1 ]'
        expected = ['[', '0', '1', ']']
        actual = lexer.lex(program)
        self.assertListEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
