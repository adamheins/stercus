#!/usr/bin/env python

import unittest
import testutil

testutil.insert_path()

from stercus import compiler

INIT = """#include <stdio.h>
          #include <stdlib.h>
          unsigned char *d0;"""

MAIN_START = """int main(void) {
                  d0=(unsigned char *)calloc(10000, 1);"""

MAIN_END = """free(d0);
              return 0;
            }"""

def sanitize(value):
    """ Sanitize program strings to make them easier to compare. """
    return ''.join(value.split())

def boil(main, other=[]):
    """ Add boilerplate to the program body. """
    return INIT + ''.join(other) + MAIN_START + main + MAIN_END

class CompilerTest(unittest.TestCase):
    def tearDown(self):
        actual = compiler.compile(self.app_table)
        self.assertEqual(sanitize(actual), sanitize(self.expected))

    def test_compile_empty(self):
        self.app_table = {'main': []}
        self.expected = boil('')

    def test_compile_increment(self):
        self.app_table = {'main': ['[', '0', '+', ']']}
        self.expected = boil('d0[0]++;')

    def test_compile_decrement(self):
        self.app_table = {'main': ['[', '0', '-', ']']}
        self.expected = boil('d0[0]--;')

    def test_compile_assigment(self):
        self.app_table = {'main': ['[', '0', '13', ']']}
        self.expected = boil('d0[0] = 13;')

    def test_compile_input(self):
        self.app_table = {'main': ['[', '0', ',', ']']}
        self.expected = boil('d0[0] = getchar();')

    def test_compile_output(self):
        self.app_table = {'main': ['[', '0', '.', ']']}
        self.expected = boil('putchar(d0[0]);')

    def test_compile_multi_applicator(self):
        self.app_table = {'main': ['[', '0', '.', ']']}
        self.expected = boil('putchar(d0[0]);')

    def test_compile_assign_from_variable(self):
        self.app_table = {'main': ['[', '0', '[', '1', ']', ']']}
        self.expected = boil('d0[0] = d0[1];')

    def test_compile_simple_conditional(self):
        self.app_table = {'main': ['(', '0', '[', '0', '.', ']', ')']}
        self.expected = boil('''while(1) {
                                  if (!d0[0]) { break; }
                                  putchar(d0[0]);
                                }''')

    def test_compile_nested_conditional(self):
        self.app_table = {'main': ['(', '0', '(', '1', '[', '0', '[', '1', ']',
                                   ']', ')', ')']}
        self.expected = boil('''while(1) {
                                  if (!d0[0]) { break; }
                                  while (1) {
                                    if (!d0[1]) { break; }
                                    d0[0] = d0[1];
                                  }
                                }''')

class CompilerCustomApplicationTest(unittest.TestCase):
    def test_compile_single_custom_application(self):
        self.app_table = {
            'inc': ['[', 's0', '+', ']'],
            'main': ['[', '0', 'inc', ']'],
        }
        actual = sanitize(compiler.compile(self.app_table))

        self.assertIn(sanitize('void inc(unsigned int s0);'), actual)
        self.assertIn(sanitize('void inc(unsigned int s0) { d0[s0]++; }'),
                      actual)
        self.assertIn(sanitize('inc(0);'), actual)

    def test_compile_multiple_custom_application(self):
        self.app_table = {
            'dec': ['[', 's0', '-', ']'],
            'inc': ['[', 's0', '+', ']'],
            'main': ['[', '0', 'inc', ']'],
        }
        actual = sanitize(compiler.compile(self.app_table))

        self.assertIn(sanitize('void inc(unsigned int s0);'), actual)
        self.assertIn(sanitize('void dec(unsigned int s0);'), actual)
        self.assertIn(sanitize('void inc(unsigned int s0) { d0[s0]++; }'),
                      actual)
        self.assertIn(sanitize('void dec(unsigned int s0) { d0[s0]--; }'),
                      actual)
        self.assertIn(sanitize('inc(0);'), actual)

    def test_compile_multiple_custom_application_with_reference(self):
        self.app_table = {
            'inc': ['[', 's0', '+', ']'],
            'foo': ['[', 's0', 'inc', ']'],
            'main': ['[', '0', 'foo', ']'],
        }
        actual = sanitize(compiler.compile(self.app_table))

        self.assertIn(sanitize('void inc(unsigned int s0);'), actual)
        self.assertIn(sanitize('void foo(unsigned int s0);'), actual)
        self.assertIn(sanitize('void inc(unsigned int s0) { d0[s0]++; }'),
                      actual)
        self.assertIn(sanitize('void foo(unsigned int s0) { inc(s0); }'),
                      actual)
        self.assertIn(sanitize('foo(0);'), actual)

if __name__ == '__main__':
    unittest.main()
