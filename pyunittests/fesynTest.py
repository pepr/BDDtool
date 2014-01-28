#!python3
# -*- coding: utf-8 -*-
import os
import textwrap
import unittest

import sys
sys.path.append('..')

import fesyn

class SyntaxFeatureTests(unittest.TestCase):
    '''Testing syntax analysis for the .feature test sources.'''


    def test_empty(self):
        '''empty .feature test source'''

        source = ''
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        sa.lex()                # prepare the first lexical token
        self.assertRaises(RuntimeError, sa.Start)


    def test_title_only(self):
        '''The feature or story title only, no section or scenario def.'''

        source = 'Feature: feature title'
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        sa.lex()                # prepare the first lexical token
        lst = list(sa.Start())
        print(lst)
        self.assertEqual(len(lst), 1)
        self.assertEqual(lst, [('feature', 'feature identifier')])

        source = 'Story: story title'
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        sa.lex()                # prepare the first lexical token
        lst = list(sa.Start())
        print(lst)
        self.assertEqual(len(lst), 1)
        self.assertEqual(lst, [('story', 'story identifier')])


if __name__ == '__main__':
    unittest.main()