#!python3
# -*- coding: utf-8 -*-
import os
import textwrap
import unittest

import felex

class LexAnalyzerForFeatureTests(unittest.TestCase):
    '''Testing lex analyzer for the .feature BDD sources.'''

    def test_empty_source(self):
        '''empty source for lexical analysis'''

        source = ''   # empty string as a source
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 1)
        self.assertEqual(lst[0], ('endofdata', None, None, None))


    def test_story_or_feature(self):
        '''story or feature recognition inside the comment'''

        # Story with no text
        source = 'Story:'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', '', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Story with text
        source = 'Story: text'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'text', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Story with text and extra spaces
        source = '      Story:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])

        # User story as the alternative to Story.
        source = 'User story: text'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'text', source, None),
                               ('endofdata', None, None, None)
                              ])

        # User story as the alternative to Story.
        source = 'User story: text'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'text', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Feature with no text
        source = 'Feature:'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', '', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Feature with text
        source = 'Feature: text'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'text', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Feature with text and extra spaces
        source = '      Feature:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Czech story with text and extra spaces
        source = '      Požadavek:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])

        source = '      Uživatelský    požadavek:   text and extra   '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Czech feature with text and extra spaces
        source = '      Rys:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])


    def test_testcase_and_scenario(self):
        '''recognizing test_case and scenario lines'''

        # Test with no text
        source = 'Test:'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('test_case', '', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Test with text
        source = 'Test: text'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('test_case', 'text', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Test with text and extra spaces
        source = '      Test:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('test_case', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Test with text and tags
        source = 'Test: text [tag1][tag2]'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('test_case', 'text', source, '[tag1][tag2]'),
                               ('endofdata', None, None, None)
                              ])

        # Scenario with no text
        source = 'Scenario:'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('scenario', '', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Scenario with text
        source = 'Scenario: text'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('scenario', 'text', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Scenario with text and extra spaces
        source = '      Scenario:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('scenario', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Scenario with text and tags
        source = 'Scenario: text [tag1][tag2]'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('scenario', 'text', source, '[tag1][tag2]'),
                               ('endofdata', None, None, None)
                              ])

        # Czech scenario with text and extra spaces
        source = '      Scénář:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('scenario', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])



    def test_given(self):
        '''recognizing various GIVEN descriptions'''

        # Given with no text
        source = 'Given:'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('given', '', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Given with text
        source = 'Given: text'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('given', 'text', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Given with text and extra spaces
        source = '      Given:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('given', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Given with text and tags -- they are not recognized. They
        # are just a part of the text.
        source = 'Given: text [tag1][tag2]'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('given', 'text [tag1][tag2]', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Czech given with text and extra spaces
        source = '      Dáno:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('given', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])


    def test_when(self):
        '''recognizing various WHEN descriptions'''

        # When with no text
        source = 'When:'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('when', '', source, None),
                               ('endofdata', None, None, None)
                              ])

        # When with text
        source = 'When: text'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('when', 'text', source, None),
                               ('endofdata', None, None, None)
                              ])

        # When with text and extra spaces
        source = '      When:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('when', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])

        # When with text and tags -- they are not recognized. They
        # are just a part of the text.
        source = 'When: text [tag1][tag2]'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('when', 'text [tag1][tag2]', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Czech when with text and extra spaces
        source = '      Když:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('when', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])


    def test_then(self):
        '''recognizing various THEN descriptions'''

        # Then with no text
        source = 'Then:'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('then', '', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Then with text
        source = 'Then: text'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('then', 'text', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Then with text and extra spaces
        source = '      Then:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('then', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Then with text and tags -- they are not recognized. They
        # are just a part of the text.
        source = 'Then: text [tag1][tag2]'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('then', 'text [tag1][tag2]', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Czech then with text and extra spaces
        source = '      Pak:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('then', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])


    def test_and(self):
        '''recognizing various AND descriptions'''

        # And with no text
        source = 'And:'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('and', '', source, None),
                               ('endofdata', None, None, None)
                              ])

        # And with text
        source = 'And: text'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('and', 'text', source, None),
                               ('endofdata', None, None, None)
                              ])

        # And with text and extra spaces
        source = '      And:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('and', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])

        # And with text and tags -- they are not recognized. They
        # are just a part of the text.
        source = 'And: text [tag1][tag2]'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('and', 'text [tag1][tag2]', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Czech and with text and extra spaces
        source = '      a:              text and extra      '
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('and', 'text and extra', source, None),
                               ('endofdata', None, None, None)
                              ])


if __name__ == '__main__':
    unittest.main()