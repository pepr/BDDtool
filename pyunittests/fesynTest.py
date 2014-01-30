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


        source = textwrap.dedent('''\
            Story: story title

            As a user
            I want the feature
            so that my life is to be easier.

            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 2)
        self.assertEqual(tree, [
            ('story', 'story title'),
            ('description',
            '\nAs a user\nI want the feature\nso that my life is to be easier.\n\n')
        ])


    def test_scenario_only(self):
        '''Scenario only'''

        source = 'Scenario: scenario identifier'
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [])
        ])


    def test_scenario_given(self):
        '''Scenario, given, but no when and then'''

        source = textwrap.dedent('''\
            Scenario: scenario identifier
               Given: given identifier
            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                ])
            ])
        ])


#    def test_scenario_given_list(self):
#        '''Scenario, given, but no when and then'''
#
#        source = textwrap.dedent('''\
#            Scenario: scenario identifier
#               Given: given identifier
#               Given: given identifier 2
#            ''')
#        sa = fesyn.SyntacticAnalyzerForFeature(source)
#        tree = sa.Start()
#        self.assertEqual(len(tree), 1)
#        self.assertEqual(tree, [
#            ('scenario', 'scenario identifier', [
#                ('given', 'given identifier', []),
#                ('given', 'given identifier 2', []),
#            ])
#        ])


#    def test_scenario_given_when(self):
#        '''Scenario, given, when, but no then'''
#
#        source = textwrap.dedent('''\
#            Scenario: scenario identifier
#               Given: given identifier
#                When: when identifier''')
#        sa = fesyn.SyntacticAnalyzerForFeature(source)
#        tree = sa.Start()
#        print(tree)
#        self.assertEqual(len(tree), 1)
#        self.assertEqual(tree, [
#            ('scenario', 'scenario identifier', [
#                ('given', 'given identifier', [
#                    ('when', 'when identifier', [])
#                ])
#            ])
#        ])


    def test_scenario_given_when_then(self):
        '''Scenario, given, when, then'''

        source = textwrap.dedent('''\
            Scenario: scenario identifier
               Given: given identifier
                When: when identifier
                Then: then identifier''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                    ('when', 'when identifier', [
                        ('then', 'then identifier', [
                        ])
                    ])
                ])
            ])
        ])
    def test_case_only(self):
        '''test case only'''

        source = textwrap.dedent('Test: test identifier')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('test_case', 'test identifier', [])
        ])


    def test_story_scenario_given_when_then_strict_format(self):
        '''Scenario, given, when, then -- strict format.'''

        source = textwrap.dedent('''\
            Story: story identifier

            As a user
            I want the feature
            so that my life is to be easier.

            Scenario: scenario identifier
               Given: given identifier
                When: when identifier
                Then: then identifier
            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        ##print(tree)
        self.assertEqual(len(tree), 3)
        self.assertEqual(tree, [
            ('story', 'story identifier'),
            ('description',
            '\nAs a user\nI want the feature\nso that my life is to be easier.\n'),
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                    ('when', 'when identifier', [
                        ('then', 'then identifier', [
                        ])
                    ])
                ])
            ])
        ])


if __name__ == '__main__':
    unittest.main()