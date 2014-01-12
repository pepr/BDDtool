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

        #---------------------------------------------------------------
        # C++ comments, i.e. starting with //
        #
        # The shortest comment (empty) till the end of data.
        source = '//'
        lst = list(lexan.Container(source))
        self.assertEqual(len(lst), 1)   # single item
        item = lst[0]          # (symbol, lexem, pre)
        self.assertEqual(item, ('comment', '', '//', None) )

        # Empty comment till the end of line (newline included).
        source = '//\n'
        lst = list(lexan.Container(source))
        self.assertEqual(len(lst), 1)   # single item
        item = lst[0]          # (symbol, lexem, pre)
        self.assertEqual(item, ('comment', '\n', '//', None) )

        # Non-empty comment with spaces in front of it.
        source = ' // a comment \n'
        lst = list(lexan.Container(source))
        self.assertEqual(len(lst), 1)   # single item
        item = lst[0]          # (symbol, lexem, pre)
        self.assertEqual(item, ('comment', ' a comment \n', ' //', None) )

        # Two comments with spaces (two lines).
        source = ' // a comment 1 \n // a comment 2 \n'
        lst = list(lexan.Container(source))
        self.assertEqual(len(lst), 2)   # two items
        self.assertEqual(lst[0], ('comment', ' a comment 1 \n', ' //', None) )
        self.assertEqual(lst[1], ('comment', ' a comment 2 \n', ' //', None) )

        #---------------------------------------------------------------
        # C comments, i.e. /* ... */
        #
        # The shortest unclosed comment till the end of data (error).
        source = '/*'
        lst = list(lexan.Container(source))
        self.assertEqual(len(lst), 1)   # one error item
        self.assertEqual(lst[0], ('error',
                                  "'*/' expected",
                                  "('comment', '', '/*', None)",
                                  None) )

        # The shortest comment (empty) till the end of data.
        source = '/**/'
        lst = list(lexan.Container(source))
        self.assertEqual(len(lst), 1)   # two items
        self.assertEqual(lst[0], ('comment', '', '/*', '*/') )

        # Empty comment till the end of line (newline).
        source = '/**/\n'
        lst = list(lexan.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst[0], ('comment', '', '/*', '*/') )
        self.assertEqual(lst[1], ('emptyline', '\n', '', None) )

        # Empty comment till the end of line -- newline and space.
        source = '/**/\n '
        lst = list(lexan.Container(source))
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst[0], ('comment', '', '/*', '*/') )
        self.assertEqual(lst[1], ('emptyline', '\n', '', None) )
        self.assertEqual(lst[2], ('skip', ' ', '', None) )

        # Empty comment till the end of line -- space and newline.
        source = '/**/ \n'
        lst = list(lexan.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst[0], ('comment', '', '/*', '*/') )
        self.assertEqual(lst[1], ('emptyline', ' \n', '', None) )

        # Non-empty comment with spaces.
        source = ' /* a comment */'
        lst = list(lexan.Container(source))
        self.assertEqual(len(lst), 1)   # single item
        self.assertEqual(lst[0], ('comment', ' a comment ', ' /*', '*/') )

        # A comment with spaces -- three lines.
        source = ' /* a comment 1 \n    a comment 2 \n */'
        lst = list(lexan.Container(source))
        self.assertEqual(len(lst), 1)
        self.assertEqual(lst[0], ('comment',
                         ' a comment 1 \n    a comment 2 \n ',
                         ' /*', '*/') )

        # A comment with extra stars.
        source = '/*** a comment ***/'
        lst = list(lexan.Container(source))
        self.assertEqual(len(lst), 1)   # single item
        self.assertEqual(lst[0], ('comment', '** a comment **', '/*', '*/') )

        # A comment with stars inside (separated from open/close sequences.
        source = '/* * * a comment * * */'
        lst = list(lexan.Container(source))
        self.assertEqual(len(lst), 1)   # single item
        self.assertEqual(lst[0], ('comment', ' * * a comment * * ', '/*', '*/') )


    def test_keywords(self):
        '''Catch identifiers considered keywords.'''

        def chk(keyword, expected_lexid): # aux. function for checking keywords
            lst = list(lexcatch.Container(keyword))
            self.assertEqual(len(lst), 1)
            lexid, value = lst[0]
            return lexid == expected_lexid and keyword == value

        # Keywords as exact strings with the exact case.
        lst = list(lexan.Container('SCENARIO'))
        self.assertEqual(len(lst), 1)   # single item
        self.assertEqual(lst[0], ('scenario', 'SCENARIO', '', None) )

        lst = list(lexan.Container('GIVEN'))
        self.assertEqual(len(lst), 1)   # single item
        self.assertEqual(lst[0], ('given', 'GIVEN', '', None) )

        lst = list(lexan.Container('WHEN'))
        self.assertEqual(len(lst), 1)   # single item
        self.assertEqual(lst[0], ('when', 'WHEN', '', None) )

        lst = list(lexan.Container('THEN'))
        self.assertEqual(len(lst), 1)   # single item
        self.assertEqual(lst[0], ('then', 'THEN', '', None) )

        lst = list(lexan.Container('TEST_CASE'))
        self.assertEqual(len(lst), 1)   # single item
        self.assertEqual(lst[0], ('test_case', 'TEST_CASE', '', None) )

        lst = list(lexan.Container('SECTION'))
        self.assertEqual(len(lst), 1)   # single item
        self.assertEqual(lst[0], ('section', 'SECTION', '', None) )

        # Keyword with spaces around.
        lst = list(lexan.Container(' SCENARIO '))
        self.assertEqual(len(lst), 2)   # two items
        self.assertEqual(lst[0], ('scenario', 'SCENARIO', ' ', None) )
        self.assertEqual(lst[1], ('skip', ' ', '', None) )



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