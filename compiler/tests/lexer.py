#!/usr/bin/env python

import unittest
import testutil

testutil.insert_path()

from stercus import lexer

class LexerTest(unittest.TestCase):
    def tearDown(self):
        actual = lexer.lex(self.program)
        self.assertListEqual(actual, self.expected)

    def test_lex_applicator(self):
        self.program = '[0 , .]'
        self.expected = ['[', '0', ',', '.', ']']

    def test_lex_conditional(self):
        self.program = '(0 [0 -])'
        self.expected = ['(', '0', '[', '0', '-', ']', ')']

    def test_lex_newline(self):
        self.program = '[0\n,]'
        self.expected = ['[', '0', ',', ']']

    def test_lex_large_numbers(self):
        self.program = '[10\n934]'
        self.expected = ['[', '10', '934', ']']

    def test_lex_big_whitespace(self):
        self.program = ' [\t0       1 ]   '
        self.expected = ['[', '0', '1', ']']

    def test_lex_custom_application(self):
        self.program = '{test [$ +]} [1 a]'
        self.expected = ['{', 'test', '[', '$', '+', ']', '}',
                         '[', '1', 'a', ']']

    def test_lex_mulitple_custom_application(self):
        self.program = '''{a [$ +]}
                          {b [$ -]}
                          [1 a b .]'''
        self.expected = ['{', 'a', '[', '$', '+', ']', '}',
                         '{', 'b', '[', '$', '-', ']', '}',
                         '[', '1', 'a', 'b', '.', ']']

if __name__ == '__main__':
    unittest.main()
