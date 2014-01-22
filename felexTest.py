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
        self.assertEqual(lst[0], ('endofdata', '', '', None))


    def test_story_or_feature(self):
        '''story or feature recognition inside the comment'''

        # Story with no text
        source = 'Story:'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'Story:', '', None),
                               ('endofdata', '', '', None)
                              ])


    def test_testcase_and_scenario(self):
        '''recognizing test_case and scenario lines'''

        # Test with no text
        source = 'Test:'
        lst = list(felex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('test_case', 'Test:', '', ''),
                               ('endofdata', '', '', None)
                              ])


if __name__ == '__main__':
    unittest.main()