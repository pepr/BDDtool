#!python3
# -*- coding: utf-8 -*-
import os
import textwrap
import unittest

import lexan

class LexanTests(unittest.TestCase):
    '''Testing lex analyzer for the Catch test sources.'''

    def setUp(self):
        pass


    def test_empty_source(self):
        '''empty source for lexical analysis'''
        source = ''   # empty string as a source
        lst = list(lexan.Container(source))
        self.assertEqual(len(lst), 0)


    def test_comment(self):
        '''comments'''
        
        # The shortest C++ comment till the end of the line.
        source = '//'
        lst = list(lexan.Container(source))
        print(lst)
        self.assertEqual(len(lst), 1)   # single item
        item = lst[0]          # (symbol, lexem, pre)
        self.assertEqual(item, ('comment', '//', None) )

###    def test_keywords(self):
###        '''keywords converted to lex items'''
###
###        def chk(keyword, expected_lexid): # aux. function for checking keywords
###            lst = list(lexcatch.Container(keyword))
###            self.assertEqual(len(lst), 1)
###            lexid, value = lst[0]
###            return lexid == expected_lexid and keyword == value
###
###        # Keywords as exact strings with the exact case.
###        self.assertTrue(chk('SCENARIO',  'kw_scenario'))
###        self.assertTrue(chk('GIVEN',     'kw_given'))
###        self.assertTrue(chk('WHEN',      'kw_when'))
###        self.assertTrue(chk('THEN',      'kw_then'))
###        self.assertTrue(chk('TEST_CASE', 'kw_test_case'))
###        self.assertTrue(chk('SECTION',   'kw_section'))
###
###        # Recognized words as keywords for human text. Case ignored.
###        self.assertTrue(chk('user story',   'lab_story'))
###        self.assertTrue(chk('USER STORY',   'lab_story'))
###        self.assertTrue(chk('UsEr StOrY',   'lab_story'))
###        self.assertTrue(chk('USER                 STORY',   'lab_story'))
###        self.assertTrue(chk('story', 'lab_story'))
###        self.assertTrue(chk('Story', 'lab_story'))
###        self.assertTrue(chk('STORY', 'lab_story'))
###        self.assertTrue(chk('StOrY', 'lab_story'))
###
###        self.assertTrue(chk('Uživatelský požadavek', 'lab_story'))
###        self.assertTrue(chk('UŽIVATELSKÝ POŽADAVEK', 'lab_story'))
###        self.assertTrue(chk('UžIvAtElSkÝ PoŽaDaVeK', 'lab_story'))
###        self.assertTrue(chk('Uživatelský požadavek', 'lab_story'))
###        self.assertTrue(chk('POŽADAVEK', 'lab_story'))
###        self.assertTrue(chk('PoŽaDaVeK', 'lab_story'))
###
###        self.assertTrue(chk('feature', 'lab_feature'))
###        self.assertTrue(chk('Feature', 'lab_feature'))
###        self.assertTrue(chk('FEATURE', 'lab_feature'))
###        self.assertTrue(chk('FeAtUrE', 'lab_feature'))
###
###        self.assertTrue(chk('rys', 'lab_feature'))
###
###    def test_body(self):
###        '''parsing the body in curly braces'''
###
###        def lex(source):   # auxiliary fn for testing lex analysis
###            return list(lexcatch.Container(source))
###
###        # Empty body.
###        source = '{}'
###        lexlst = lex(source)
###        self.assertTrue(lexlst == [('lbrace', '{'), ('rbrace', '}')])
###
###        # Empty body with newline.
###        source = '{\n}'
###        lexlst = lex(source)
###        self.assertTrue(lexlst == [('lbrace',  '{'),
###                                   ('newline', '\n'),
###                                   ('rbrace',  '}')])
###
###        # Empty body with trivial C comment.
###        source = '{/**/}'
###        lexlst = lex(source)
###        self.assertTrue(lexlst == [('lbrace',  '{'),
###                                   ('commentlpar', '/*'),
###                                   ('commentrpar', '*/'),
###                                   ('rbrace',  '}')])
###
###
###    def test_SECTION(self):
###        '''lexical parsing of SECTION constructs.'''
###
###        def lex(source):   # auxiliary fn for testing lex analysis
###            return list(lexcatch.Container(source))
###
###        # The smallest SECTION with body (empty identification string,
###        # and empty body on one line).
###        source = 'SECTION(""){}'
###        lexlst = lex(source)
###        self.assertTrue(lexlst == [('kw_section', 'SECTION'),
###                                   ('lpar',       '('),
###                                   ('dquote',     '"'),
###                                   ('dquote',     '"'),
###                                   ('rpar',       ')'),
###                                   ('lbrace',     '{'),
###                                   ('rbrace',     '}')])
###
###        # Usual SECTION with identifier but empty body.
###        source = 'SECTION( "identifier" ) {\n}'
###        lexlst = lex(source)
###        self.assertTrue(lexlst == [('kw_section',     'SECTION'),
###                                   ('lpar',           '('),
###                                   ('whitespaces',    ' '),
###                                   ('dquote',         '"'),
###                                   ('str',            'identifier'),
###                                   ('dquote',         '"'),
###                                   ('whitespaces',    ' '),
###                                   ('rpar',           ')'),
###                                   ('whitespaces',    ' '),
###                                   ('lbrace',         '{'),
###                                   ('newline',        '\n'),
###                                   ('rbrace',         '}')
###                                  ])
###
###

if __name__ == '__main__':
    unittest.main()