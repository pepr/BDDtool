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


    def test_story_or_feature(self):
        '''story or feature recognition inside the comment'''

        # Story
        source = '// Story: story identifier'   # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', '// Story: ', None),
                               ('endofdata', '', '', None)
                              ])

        source = '// Story: story identifier '  # with trailing space
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', '// Story: ', ' '),
                               ('endofdata', '', '', None)
                              ])

        source = '// Story: story identifier\n' # with newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', '// Story: ', '\n'),
                               ('endofdata', '', '', None)
                              ])

        source = '// Story: story identifier \n' # with trailing space and newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', '// Story: ', ' \n'),
                               ('endofdata', '', '', None)
                              ])

        # Feature
        source = '// Feature: feature identifier'   # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'feature identifier', '// Feature: ', None),
                               ('endofdata', '', '', None)
                              ])

        source = '// Feature: feature identifier\n' # with newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'feature identifier', '// Feature: ', '\n'),
                               ('endofdata', '', '', None)
                              ])

        source = '// Feature: feature identifier \n' # with trailing space and newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'feature identifier', '// Feature: ', ' \n'),
                               ('endofdata', '', '', None)
                              ])

        # UsEr StOrY
        source = '// UsEr StOrY: story identifier'      # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', '// UsEr StOrY: ', None),
                               ('endofdata', '', '', None)
                              ])

        source = '// UsEr StOrY: story identifier\n'    # with newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', '// UsEr StOrY: ', '\n'),
                               ('endofdata', '', '', None)
                              ])

        # Czech equivalents.
        source = '// PoŽadavek: identifikace požadavku' # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'identifikace požadavku', '// PoŽadavek: ', None),
                               ('endofdata', '', '', None)
                              ])

        source = '// rys: identifikace rysu'            # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'identifikace rysu', '// rys: ', None),
                               ('endofdata', '', '', None)
                              ])


        # C-comment.
        source = '/* Story: story identifier */'        # single line
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', '/* Story: ', ' */'),
                               ('endofdata', '', '', None)
                              ])


        # Multiline C-comment.
        source = '/*\n Story: story identifier \n  comment2 \n comment3 \n*/'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', '/*\n Story: ',
                                             ' \n  comment2 \n comment3 \n'),
                               ('endofdata', '', '', None)
                              ])


if __name__ == '__main__':
    unittest.main()