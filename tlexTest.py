#!python3
# -*- coding: utf-8 -*-
import os
import textwrap
import unittest

import tlex

class LexAnalyzerForCatchTests(unittest.TestCase):
    '''Testing lex analyzer for the Catch test sources.'''

    def test_empty_source(self):
        '''empty source for lexical analysis'''

        source = ''   # empty string as a source
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 1)
        self.assertEqual(lst[0], ('endofdata', '', '', None))


    def test_comment(self):
        '''comments'''

        #---------------------------------------------------------------
        # C++ comments, i.e. starting with //
        #
        # The shortest comment (empty) till the end of data.
        source = '//'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', '', '//', None),
                               ('endofdata', '', '', None)
                              ])

        # Empty comment till the end of line (newline included).
        source = '//\n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', '\n', '//', None),
                               ('endofdata', '', '', None)
                              ])

        # Non-empty comment without newline.
        source = '// a comment'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', ' a comment', '//', None),
                               ('endofdata', '', '', None)
                              ])

        # Non-empty comment with newline.
        source = '// a comment \n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', ' a comment \n', '//', None),
                               ('endofdata', '', '', None)
                              ])

        # Two comments with spaces (two lines).
        source = ' // a comment 1 \n // a comment 2 \n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst, [('comment', ' a comment 1 \n', ' //', None),
                               ('comment', ' a comment 2 \n', ' //', None),
                               ('endofdata', '', '', None)
                              ])

        #---------------------------------------------------------------
        # C comments, i.e. /* ... */
        #
        # The shortest unclosed comment till the end of data (error).
        source = '/*'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)   # one error item plus endofdata
        self.assertEqual(lst, [('error', "'*/' expected",
                                 "('comment', '', '/*', None)", None),
                               ('endofdata', '', '', None)
                              ])

        # The shortest comment (empty) till the end of data.
        source = '/**/'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', '', '/*', '*/'),
                               ('endofdata', '', '', None)
                              ])

        # Empty comment till the end of line (newline).
        source = '/**/\n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst, [('comment', '', '/*', '*/'),
                               ('emptyline', '\n', '', None),
                               ('endofdata', '', '', None)
                              ])

        # Empty comment till the end of line -- newline and space.
        source = '/**/\n '
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst, [('comment', '', '/*', '*/'),
                               ('emptyline', '\n', '', None),
                               ('endofdata', '', ' ', None)
                              ])

        # Empty comment till the end of line -- space and newline.
        source = '/**/ \n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst, [('comment', '', '/*', '*/'),
                               ('emptyline', ' \n', '', None),
                               ('endofdata', '', '', None)
                              ])

        # Non-empty comment with spaces.
        source = ' /* a comment */'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', ' a comment ', ' /*', '*/'),
                               ('endofdata', '', '', None)
                              ])

        # A comment with spaces -- three lines.
        source = ' /* a comment 1 \n    a comment 2 \n */'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment',
                                ' a comment 1 \n    a comment 2 \n ',
                                ' /*', '*/'),
                               ('endofdata', '', '', None)
                              ])

        # A comment with extra stars.
        source = '/*** a comment ***/'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', '** a comment **', '/*', '*/'),
                               ('endofdata', '', '', None)
                              ])

        # A comment with stars inside (separated from open/close sequences.
        source = '/* * * a comment * * */'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', ' * * a comment * * ', '/*', '*/'),
                               ('endofdata', '', '', None)
                              ])


    def test_keywords(self):
        '''Catch identifiers considered keywords.'''

        # Keywords as exact strings with the exact case.
        lst = list(tlex.Container('SCENARIO'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('scenario', 'SCENARIO', '', None),
                               ('endofdata', '', '', None)
                              ])

        lst = list(tlex.Container('GIVEN'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('given', 'GIVEN', '', None),
                               ('endofdata', '', '', None)
                              ])

        lst = list(tlex.Container('WHEN'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('when', 'WHEN', '', None),
                               ('endofdata', '', '', None)
                              ])

        lst = list(tlex.Container('THEN'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('then', 'THEN', '', None),
                               ('endofdata', '', '', None)
                              ])

        lst = list(tlex.Container('TEST_CASE'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('test_case', 'TEST_CASE', '', None),
                               ('endofdata', '', '', None)
                              ])

        lst = list(tlex.Container('SECTION'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('section', 'SECTION', '', None),
                               ('endofdata', '', '', None)
                              ])

        # Keyword with spaces around.
        lst = list(tlex.Container(' SCENARIO '))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('scenario', 'SCENARIO', ' ', None),
                               ('endofdata', '', ' ', None)
                              ])


    def test_string_literals(self):
        '''recognizing string literals

        String literals are considered test/section identifiers for Catch.
        '''

        # Empty string literal.
        source = '""'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', '', '"', '"'),
                               ('endofdata', '', '', None)
                              ])

        # Simple string literal.
        source = '"simple"'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', 'simple', '"', '"'),
                               ('endofdata', '', '', None)
                              ])

        source = '"words and spaces"'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', 'words and spaces', '"', '"'),
                               ('endofdata', '', '', None)
                              ])

        # Escaped double quote.
        source = r'"\""'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', r'\"', '"', '"'),
                               ('endofdata', '', '', None)
                              ])

        # Escaped tab.
        source = r'"\t"'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', r'\t', '"', '"'),
                               ('endofdata', '', '', None)
                              ])

        # Escaped newline.
        source = r'"\n"'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', r'\n', '"', '"'),
                               ('endofdata', '', '', None)
                              ])

        # Not closed literal.
        source = r'"not closed'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('error', '\'"\' expected',
               '(\'stringlit\', \'not closed\', \'"\', None)', None),
                               ('endofdata', '', '', None)
                              ])



    def test_terminals(self):
        '''recognizing one-char terminal symbols'''

        source = '('
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]          # (symbol, lexem, pre, post)
        self.assertEqual(item, ('lpar', '(', '', None) )

        source = '\t('
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('lpar', '(', '\t', None) )

        source = ')'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('rpar', ')', '', None) )

        source = '{'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('lbrace', '{', '', None) )

        source = '}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('rbrace', '}', '', None) )

        source = ','
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('comma', ',', '', None) )


    def test_simple_testcase_and_sections(self):
        '''recognizing simple sections with empty body (lexical)'''

        source = 'TEST_CASE("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('test_case', 'TEST_CASE', '', None),
                               ('lpar', '(', '', None),
                               ('stringlit', 'identifier', '"', '"'),
                               ('rpar', ')', '', None),
                               ('lbrace', '{', '', None),
                               ('rbrace', '}', '', None),
                               ('endofdata', '', '', None)
                              ])

        source = 'SCENARIO("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('scenario', 'SCENARIO', '', None),
                               ('lpar', '(', '', None),
                               ('stringlit', 'identifier', '"', '"'),
                               ('rpar', ')', '', None),
                               ('lbrace', '{', '', None),
                               ('rbrace', '}', '', None),
                               ('endofdata', '', '', None)
                              ])

        source = 'SECTION("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('section', 'SECTION', '', None),
                               ('lpar', '(', '', None),
                               ('stringlit', 'identifier', '"', '"'),
                               ('rpar', ')', '', None),
                               ('lbrace', '{', '', None),
                               ('rbrace', '}', '', None),
                               ('endofdata', '', '', None)
                              ])

        source = 'GIVEN("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('given', 'GIVEN', '', None),
                               ('lpar', '(', '', None),
                               ('stringlit', 'identifier', '"', '"'),
                               ('rpar', ')', '', None),
                               ('lbrace', '{', '', None),
                               ('rbrace', '}', '', None),
                               ('endofdata', '', '', None)
                              ])

        source = 'WHEN("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('when', 'WHEN', '', None),
                               ('lpar', '(', '', None),
                               ('stringlit', 'identifier', '"', '"'),
                               ('rpar', ')', '', None),
                               ('lbrace', '{', '', None),
                               ('rbrace', '}', '', None),
                               ('endofdata', '', '', None)
                              ])

        source = 'THEN("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('then', 'THEN', '', None),
                               ('lpar', '(', '', None),
                               ('stringlit', 'identifier', '"', '"'),
                               ('rpar', ')', '', None),
                               ('lbrace', '{', '', None),
                               ('rbrace', '}', '', None),
                               ('endofdata', '', '', None)
                              ])

        source = 'AND_THEN("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('and_then', 'AND_THEN', '', None),
                               ('lpar', '(', '', None),
                               ('stringlit', 'identifier', '"', '"'),
                               ('rpar', ')', '', None),
                               ('lbrace', '{', '', None),
                               ('rbrace', '}', '', None),
                               ('endofdata', '', '', None)
                              ])

        source = 'AND_WHEN("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('and_when', 'AND_WHEN', '', None),
                               ('lpar', '(', '', None),
                               ('stringlit', 'identifier', '"', '"'),
                               ('rpar', ')', '', None),
                               ('lbrace', '{', '', None),
                               ('rbrace', '}', '', None),
                               ('endofdata', '', '', None)
                              ])


#    def test_story_or_feature(self):
#        '''story or feature recognition inside the comment'''
#
#        def chk(keyword, expected_lexid): # aux. function for checking keywords
#            lst = list(tlex.Container(keyword))
#            self.assertEqual(len(lst), 1)
#            lexid, value = lst[0]
#            return lexid == expected_lexid and keyword == value
#
#        # Recognized words as keywords for human text. Case ignored.
#        self.assertTrue(chk('user story',   'story'))
#        self.assertTrue(chk('USER STORY',   'story'))
#        self.assertTrue(chk('UsEr StOrY',   'story'))
#        self.assertTrue(chk('USER                 STORY',   'story'))
#        self.assertTrue(chk('story', 'story'))
#        self.assertTrue(chk('Story', 'story'))
#        self.assertTrue(chk('STORY', 'story'))
#        self.assertTrue(chk('StOrY', 'story'))
#
#        self.assertTrue(chk('Uživatelský požadavek', 'story'))
#        self.assertTrue(chk('UŽIVATELSKÝ POŽADAVEK', 'story'))
#        self.assertTrue(chk('UžIvAtElSkÝ PoŽaDaVeK', 'story'))
#        self.assertTrue(chk('Uživatelský požadavek', 'story'))
#        self.assertTrue(chk('POŽADAVEK', 'story'))
#        self.assertTrue(chk('PoŽaDaVeK', 'story'))
#
#        self.assertTrue(chk('feature', 'feature'))
#        self.assertTrue(chk('Feature', 'feature'))
#        self.assertTrue(chk('FEATURE', 'feature'))
#        self.assertTrue(chk('FeAtUrE', 'feature'))
#
#        self.assertTrue(chk('rys', 'feature'))


    def test_story_or_feature(self):
        '''story or feature recognition inside the comment'''

        source = '// Story: story identifier\n'
        lst = list(tlex.Container(source))
        ##print('tsf:', lst)
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('story', 'story identifier', '// Story: ', '\n'))


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