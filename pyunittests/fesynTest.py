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
        tree = sa.Start()
        self.assertEqual(tree, [])


    def test_title_only(self):
        '''The feature or story title only, no section or scenario def.'''

        source = 'Feature: feature title'
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [('feature', 'feature title')])

        source = 'Story: story title'
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [('story', 'story title')])


    def test_story_with_description(self):
        '''The feature or story with a title and a description.'''

        source = textwrap.dedent('''\
            Feature: feature title

            The feature description is just some text.

            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 2)
        self.assertEqual(tree, [
            ('feature', 'feature title'),
            ('description', '\nThe feature description is just some text.\n\n')
        ])


if __name__ == '__main__':
    unittest.main()