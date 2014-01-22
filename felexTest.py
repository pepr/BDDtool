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


if __name__ == '__main__':
    unittest.main()