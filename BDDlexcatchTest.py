#!python3
# -*- coding: utf-8 -*-
import os
import textwrap
import unittest

from lexcatch import LexContainer as LC

class LexCatchTests(unittest.TestCase):
    '''Testing lex analyzer for the Catch test sources.'''

    def setUp(self):
        pass


    def test_empty_source(self):
        source = ''   # empty string as a source
        lst = list(LC(''))
        self.assertEqual(len(lst), 0)


    def check_keyword(self, k, lexitem):
        # Auxiliary function for 
        lst = list(LC(k))
        alx, ak = lst[0]
        return len(lst) == 1 and alx == lexitem and ak == k

        
    def test_keywords(self):
        '''keywords converted to lex items'''
        
        chk = self.check_keyword
        
        # Keywords as exact strings with the exact case.
        self.assertTrue(chk('SCENARIO',  'scenario'))
        self.assertTrue(chk('GIVEN',     'given'))
        self.assertTrue(chk('WHEN',      'when'))
        self.assertTrue(chk('THEN',      'then'))
        self.assertTrue(chk('TEST_CASE', 'test_case'))
        self.assertTrue(chk('SECTION',   'section'))
        
        # Recognized words as keywords for human text. Case ignored.
        self.assertTrue(chk('user story',   'story'))
        self.assertTrue(chk('USER STORY',   'story'))
        self.assertTrue(chk('UsEr StOrY',   'story'))
        self.assertTrue(chk('USER                 STORY',   'story'))
        self.assertTrue(chk('story', 'story'))
        self.assertTrue(chk('Story', 'story'))
        self.assertTrue(chk('STORY', 'story'))
        self.assertTrue(chk('StOrY', 'story'))
        
        self.assertTrue(chk('Uživatelský požadavek', 'story'))
        self.assertTrue(chk('UŽIVATELSKÝ POŽADAVEK', 'story'))
        self.assertTrue(chk('UžIvAtElSkÝ PoŽaDaVeK', 'story'))
        self.assertTrue(chk('Uživatelský požadavek', 'story'))
        self.assertTrue(chk('POŽADAVEK', 'story'))
        self.assertTrue(chk('PoŽaDaVeK', 'story'))


if __name__ == '__main__':
    unittest.main()