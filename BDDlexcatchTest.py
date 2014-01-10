#!python3
# -*- coding: utf-8 -*-
import os
import textwrap
import unittest

import lexcatch

class LexCatchTests(unittest.TestCase):
    '''Testing lex analyzer for the Catch test sources.'''

    def setUp(self):
        pass


    def test_empty_source(self):
        '''empty source for lexical analysis'''
        source = ''   # empty string as a source
        lst = list(lexcatch.Container(''))
        self.assertEqual(len(lst), 0)


    def test_keywords(self):
        '''keywords converted to lex items'''

        def chk(keyword, expected_lexid): # aux. function for checking keywords
            lst = list(lexcatch.Container(keyword))
            self.assertEqual(len(lst), 1)
            lexid, value = lst[0]
            return lexid == expected_lexid and keyword == value

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

        self.assertTrue(chk('feature', 'feature'))
        self.assertTrue(chk('Feature', 'feature'))
        self.assertTrue(chk('FEATURE', 'feature'))
        self.assertTrue(chk('FeAtUrE', 'feature'))


    def test_body(self):
        '''parsing the body in curly braces'''

        def lex(source):   # auxiliary fn for testing lex analysis
            return list(lexcatch.Container(source))

        # Empty body.
        source = '{}'
        lexlst = lex(source)
        self.assertTrue(lexlst == [('lbrace', '{'), ('rbrace', '}')])

        # Empty body with newline.
        source = '{\n}'
        lexlst = lex(source)
        self.assertTrue(lexlst == [('lbrace',  '{'),
                                   ('newline', '\n'),
                                   ('rbrace',  '}')])

        # Empty body with trivial C comment.
        source = '{/**/}'
        lexlst = lex(source)
        self.assertTrue(lexlst == [('lbrace',  '{'),
                                   ('commentlpar', '/*'),
                                   ('commentrpar', '*/'),
                                   ('rbrace',  '}')])


    def test_SECTION(self):

        def lex(source):   # auxiliary fn for testing lex analysis
            return list(lexcatch.Container(source))

        # The smallest SECTION with body (empty identification string,
        # and empty body on one line).
        source = 'SECTION(""){}'
        lexlst = lex(source)
        self.assertTrue(lexlst == [('section', 'SECTION'),
                                   ('lpar',    '('),
                                   ('dquote',  '"'),
                                   ('dquote',  '"'),
                                   ('rpar',    ')'),
                                   ('lbrace',  '{'),
                                   ('rbrace',  '}')])

        # Usual SECTION with identifier but empty body.
        source = 'SECTION( "identifier" ) {\n}'
        print(lexlst)
        self.assertTrue(lexlst == [('section',     'SECTION'),
                                   ('lpar',        '('),
                                   ('whitespaces', ' '),
                                   ('dquote',      '"'),
                                   ('str',         'identifier'),
                                   ('dquote',      '"'),
                                   ('whitespaces', ' '),
                                   ('rpar',        ')'),
                                   ('whitespaces', ' '),
                                   ('lbrace',      '{'),
                                   ('newline',     '\n'),
                                   ('rbrace',      '}')
                                  ])



if __name__ == '__main__':
    unittest.main()