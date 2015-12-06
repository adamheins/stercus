#!/usr/bin/env python

import os
import sys
import unittest

# Allow stercus module to be imported.
CUR_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CUR_DIR, os.pardir))
sys.path.insert(0, ROOT_DIR)

from stercus import parser

class ParserTest(unittest.TestCase):
    def test_parse_applicator(self):
        tokens = ['[', '0', '1', ']']
        expected = {
            'main': ['[', '0', '1', ']']
        }
        actual = parser.parse(tokens)
        self.assertDictEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
