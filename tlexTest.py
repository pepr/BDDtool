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
                                 # symbol, value, lexem, extra_info
        self.assertEqual(lst[0], ('endofdata', None, None, None))


    def test_comment(self):
        '''comments'''

        #---------------------------------------------------------------
        # C++ comments, i.e. starting with //
        #
        # The shortest comment (empty) till the end of data.
        source = '//'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', None, source, None),
                               ('endofdata', None, None, None)
                              ])

        # Empty comment till the end of line (newline included).
        source = '//\n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', None, source, None),
                               ('endofdata', None, None, None)
                              ])

        # Non-empty comment without newline.
        source = '// a comment'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', ' a comment', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Non-empty comment with newline.
        source = '// a comment \n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', ' a comment ', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Two comments with spaces (two lines).
        source = ' // a comment 1 \n // a comment 2 \n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst, [('comment', ' a comment 1 ', ' // a comment 1 \n', None),
                               ('comment', ' a comment 2 ', ' // a comment 2 \n', None),
                               ('endofdata', None, None, None)
                              ])

        #---------------------------------------------------------------
        # C comments, i.e. /* ... */
        #
        # The shortest unclosed comment till the end of data (error).
        source = '/*'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)   # one error item plus endofdata
        self.assertEqual(lst, [('error', "'*/' expected",
                                 "('comment', None, '/*', None)", None),
                               ('endofdata', None, None, None)
                              ])

        # The shortest comment (empty) till the end of data.
        source = '/**/'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', None, source, None),
                               ('endofdata', None, None, None)
                              ])

        # Empty comment till the end of line (newline).
        source = '/**/\n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst, [('comment', None, '/**/', None),
                               ('emptyline', None, '\n', None),
                               ('endofdata', None, None, None)
                              ])

        # Empty comment till the end of line -- newline and space.
        source = '/**/\n '
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst, [('comment', None, '/**/', None),
                               ('emptyline', None, '\n', None),
                               ('endofdata', None, ' ', None)
                              ])

        # Empty comment till the end of line -- space and newline.
        source = '/**/ \n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst, [('comment', None, '/**/', None),
                               ('emptyline', None, ' \n', None),
                               ('endofdata', None, None, None)
                              ])

        # Non-empty comment with spaces.
        source = ' /* a comment */'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', ' a comment ', source, None),
                               ('endofdata', None, None, None)
                              ])

        # A comment with spaces -- three lines.
        source = ' /* a comment 1 \n    a comment 2 \n */'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', ' a comment 1 \n    a comment 2 \n ',
                                source, None),
                               ('endofdata', None, None, None)
                              ])

        # A comment with extra stars.
        source = '/*** a comment ***/'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', '** a comment **', source, None),
                               ('endofdata', None, None, None)
                              ])

        # A comment with stars inside (separated from open/close sequences.
        source = '/* * * a comment * * */'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', ' * * a comment * * ', source, None),
                               ('endofdata', None, None, None)
                              ])


    def test_keywords(self):
        '''Catch identifiers considered keywords.'''

        # Keywords as exact strings with the exact case.
        lst = list(tlex.Container('SCENARIO'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('scenario', None, 'SCENARIO',None),
                               ('endofdata', None, None, None)
                              ])

        lst = list(tlex.Container('GIVEN'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('given', None, 'GIVEN', None),
                               ('endofdata', None, None, None)
                              ])

        lst = list(tlex.Container('WHEN'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('when', None, 'WHEN', None),
                               ('endofdata', None, None, None)
                              ])

        lst = list(tlex.Container('THEN'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('then', None, 'THEN', None),
                               ('endofdata', None, None, None)
                              ])

        lst = list(tlex.Container('TEST_CASE'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('test_case', None, 'TEST_CASE',None),
                               ('endofdata', None, None, None)
                              ])

        lst = list(tlex.Container('SECTION'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('section', None, 'SECTION', None),
                               ('endofdata', None, None, None)
                              ])

        # Keyword with spaces around.
        lst = list(tlex.Container(' SCENARIO '))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('scenario', None, ' SCENARIO', None),
                               ('endofdata', None, ' ', None)
                              ])


    def test_string_literals(self):
        '''recognizing string literals

        String literals are considered test/section identifiers for Catch.
        '''

        # Empty string literal.
        source = '""'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', '', '""', None),
                               ('endofdata', None, None, None)
                              ])

        # Simple string literal.
        source = '"simple"'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', 'simple', source, None),
                               ('endofdata', None, None, None)
                              ])

        source = '"words and spaces"'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', 'words and spaces', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Escaped double quote.
        source = r'"\""'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', r'\"', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Escaped tab.
        source = r'"\t"'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', r'\t', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Escaped newline.
        source = r'"\n"'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', r'\n', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Not closed literal.
        source = r'"not closed'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('error', '\'"\' expected',
                  "('stringlit', 'not closed', '\"not closed', None)", None),
                               ('endofdata', None, None, None)
                              ])


    def test_terminals(self):
        '''recognizing one-char terminal symbols'''

        source = '('
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]          # (symbol, lexem, pre, post)
        self.assertEqual(item, ('lpar', None, source, None) )

        source = '\t('
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('lpar', None, source, None) )

        source = ')'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('rpar', None, source, None) )

        source = '{'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('lbrace', None, source, None) )

        source = '}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('rbrace', None, source, None) )

        source = ','
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('comma', None, source, None) )


    def test_simple_testcase_and_sections(self):
        '''recognizing simple sections with empty body (lexical)'''

        source = 'TEST_CASE("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('test_case', None, 'TEST_CASE', None),
                               ('lpar', None, '(', None),
                               ('stringlit', 'identifier', '"identifier"', None),
                               ('rpar', None, ')', None),
                               ('lbrace', None, '{', None),
                               ('rbrace', None, '}', None),
                               ('endofdata', None, None, None)
                              ])

        source = 'SCENARIO("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('scenario', None, 'SCENARIO', None),
                               ('lpar', None, '(', None),
                               ('stringlit', 'identifier', '"identifier"', None),
                               ('rpar', None, ')', None),
                               ('lbrace', None, '{', None),
                               ('rbrace', None, '}', None),
                               ('endofdata', None, None, None)
                              ])

        source = 'SECTION("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('section', None, 'SECTION', None),
                               ('lpar', None, '(', None),
                               ('stringlit', 'identifier', '"identifier"', None),
                               ('rpar', None, ')', None),
                               ('lbrace', None, '{', None),
                               ('rbrace', None, '}', None),
                               ('endofdata', None, None, None)
                              ])

        source = 'GIVEN("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('given', None, 'GIVEN', None),
                               ('lpar', None, '(', None),
                               ('stringlit', 'identifier', '"identifier"', None),
                               ('rpar', None, ')', None),
                               ('lbrace', None, '{', None),
                               ('rbrace', None, '}', None),
                               ('endofdata', None, None, None)
                              ])

        source = 'WHEN("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('when', None, 'WHEN', None),
                               ('lpar', None, '(', None),
                               ('stringlit', 'identifier', '"identifier"', None),
                               ('rpar', None, ')', None),
                               ('lbrace', None, '{', None),
                               ('rbrace', None, '}', None),
                               ('endofdata', None, None, None)
                              ])

        source = 'THEN("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('then', None, 'THEN', None),
                               ('lpar', None, '(', None),
                               ('stringlit', 'identifier', '"identifier"', None),
                               ('rpar', None, ')', None),
                               ('lbrace', None, '{', None),
                               ('rbrace', None, '}', None),
                               ('endofdata', None, None, None)
                              ])

        source = 'AND_THEN("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('and_then', None, 'AND_THEN', None),
                               ('lpar', None, '(', None),
                               ('stringlit', 'identifier', '"identifier"', None),
                               ('rpar', None, ')', None),
                               ('lbrace', None, '{', None),
                               ('rbrace', None, '}', None),
                               ('endofdata', None, None, None)
                              ])

        source = 'AND_WHEN("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('and_when', None, 'AND_WHEN', None),
                               ('lpar', None, '(', None),
                               ('stringlit', 'identifier', '"identifier"', None),
                               ('rpar', None, ')', None),
                               ('lbrace', None, '{', None),
                               ('rbrace', None, '}', None),
                               ('endofdata', None, None, None)
                              ])


    def test_story_or_feature(self):
        '''story or feature recognition inside the comment'''

        # Story
        source = '// Story: story identifier'   # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('endofdata', None, None, None)
                              ])

        source = '// Story: story identifier '  # with trailing space
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('endofdata', None, None, None)
                              ])

        source = '// Story: story identifier\n' # with newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('endofdata', None, None, None)
                              ])

        source = '// Story: story identifier \n' # with trailing space and newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Feature
        source = '// Feature: feature identifier'   # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'feature identifier', source, None),
                               ('endofdata', None, None, None)
                              ])

        source = '// Feature: feature identifier\n' # with newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'feature identifier', source, None),
                               ('endofdata', None, None, None)
                              ])

        source = '// Feature: feature identifier \n' # with trailing space and newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'feature identifier', source, None),
                               ('endofdata', None, None, None)
                              ])

        # UsEr StOrY
        source = '// UsEr StOrY: story identifier'      # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('endofdata', None, None, None)
                              ])

        source = '// UsEr StOrY: story identifier\n'    # with newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('endofdata', None, None, None)
                              ])

        # Czech equivalents.
        source = '// PoŽadavek: identifikace požadavku' # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'identifikace požadavku', source, None),
                               ('endofdata', None, None, None)
                              ])

        source = '// rys: identifikace rysu'            # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'identifikace rysu', source, None),
                               ('endofdata', None, None, None)
                              ])


        # C-comment.
        source = '/* Story: story identifier */'        # single line
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('endofdata', None, None, None)
                              ])


        # Multiline C-comment.
        source = '/*\n Story: story identifier \n  comment2 \n comment3 \n*/'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('endofdata', None, None, None)
                              ])

        source = '/*\n Feature: feature identifier \n  comment2 \n comment3 \n*/'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'feature identifier', source, None),
                               ('endofdata', None, None, None)
                              ])


if __name__ == '__main__':
    unittest.main()