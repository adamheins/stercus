#!/usr/bin/env python

import unittest
import testutil

testutil.insert_path()

from stercus import preprocessor

class PreprocessorTest(unittest.TestCase):
    def tearDown(self):
        actual = preprocessor.preprocess(self.program).strip()
        self.assertEqual(actual, self.expected)

    def test_preprocess_comment_line(self):
        self.program = '# This is a simple comment.'
        self.expected = ''

    def test_preprocess_comment_end_of_line(self):
        self.program = '[0 1] # Comment following code.'
        self.expected = '[0 1]'

    def test_preprocess_comment_multiline(self):
        self.program = '## This is a comment\nthat spans multiple lines##'
        self.expected = ''

    def test_preprocess_internal_multiline(self):
        self.program = '[0 ## Add 1 here ## +]'
        self.expected = '[0  +]'

if __name__ == '__main__':
    unittest.main()
