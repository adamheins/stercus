#!/usr/bin/env python

import unittest
import testutil

testutil.insert_path()

from stercus import parser
from stercus import errors

class ParserTest(unittest.TestCase):
    def tearDown(self):
        actual = parser.parse(self.tokens)
        self.assertDictEqual(actual, self.expected)

    def test_parse_applicator(self):
        # [0 1]
        self.tokens = ['[', '0', '1', ']']
        self.expected = {
            'main': ['[', '0', '1', ']']
        }

    def test_parse_multi_applicator(self):
        # [0 + + +]
        self.tokens = ['[', '0', '+', '+', '+', ']']
        self.expected = {
            'main': ['[', '0', '+', '+', '+', ']']
        }

    def test_parse_conditional(self):
        # (0 [1 +])
        self.tokens = ['(', '0', '[', '1', '+', ']', ')']
        self.expected = {
            'main': ['(', '0', '[', '1', '+', ']', ')']
        }

    def test_parse_nested_conditional(self):
        # (0 (1))
        self.tokens = ['(', '0', '(', '1', ')', ')']
        self.expected = {
            'main': ['(', '0', '(', '1', ')', ')']
        }

    def test_parse_custom_application(self):
        # {a [$ +]}
        # [0 a]
        self.tokens = ['{', 'a', '[', '$', '+', ']', '}',
                       '[', '0', 'a', ']']
        self.expected = {
            'a': ['[', 's0', '+', ']'],
            'main': ['[', '0', 'a', ']'],
        }

class ParserTestInvalid(unittest.TestCase):
    def test_parse_custom_application_named_main(self):
        # {main [$ +]}
        tokens = ['{', 'main', '[', '$', '+', ']', '}']
        with self.assertRaises(errors.ApplicationNameError):
            parser.parse(tokens)

    def test_parse_custom_application_starts_with_num(self):
        # {1 [$ +]}
        tokens = ['{', '1', '[', '$', '+', ']', '}']
        with self.assertRaises(errors.ApplicationNameError):
            parser.parse(tokens)

    def test_parse_custom_application_nested(self):
        # {outer
        #   {inner [$ +]}
        # [$ inner]}
        tokens = ['{', 'outer',
                      '{', 'inner', '[', '$', '+', ']', '}',
                  '[', '$', 'inner', ']', '}']
        with self.assertRaises(errors.UnbalancedBracketsError):
            parser.parse(tokens)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ParserTest)

if __name__ == '__main__':
    unittest.main()
