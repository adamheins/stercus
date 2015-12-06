#!/usr/bin/env python

import os
import sys
import unittest

# Allow stercus module to be imported.
CUR_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CUR_DIR, os.pardir))
sys.path.insert(0, ROOT_DIR)

from stercus import preprocessor

class PreprocessorTest(unittest.TestCase):
    def test_preprocess_comment_line(self):
        program = '# This is a simple comment.'
        expected = ''
        actual = preprocessor.preprocess(program).strip()
        self.assertEqual(actual, expected)

    def test_preprocess_comment_end_of_line(self):
        program = '[0 1] # Comment following code.'
        expected = '[0 1]'
        actual = preprocessor.preprocess(program).strip()
        self.assertEqual(actual, expected)

    def test_preprocess_comment_multiline(self):
        program = '## This is a comment\nthat spans multiple lines##'
        expected = ''
        actual = preprocessor.preprocess(program).strip()
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
