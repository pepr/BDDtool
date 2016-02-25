#!python3
import os
import textwrap
import unittest

import sys
sys.path.append('..')

import tlex

class LexAnalyzerForCatchTests(unittest.TestCase):
    """Testing lex analyzer for the Catch test sources.
    """

    def test_empty_source(self):
        """empty source for lexical analysis
        """
        source = ''   # empty string as a source
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 1)
                                 # symbol, value, lexem, extra_info
        self.assertEqual(lst[0], ('$', None, None, None))


    def test_comment(self):
        """comments
        """
        #---------------------------------------------------------------
        # C++ comments, i.e. starting with //
        #
        # The shortest comment (empty) till the end of data.
        source = '//'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', '', source, None),
                               ('$', None, None, None)
                              ])

        # Empty comment till the end of line (newline included).
        source = '//\n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', '', source, None),
                               ('$', None, None, None)
                              ])

        # Non-empty comment without newline.
        source = '// a comment'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', ' a comment', source, None),
                               ('$', None, None, None)
                              ])

        # Non-empty comment with newline.
        source = '// a comment \n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', ' a comment ', source, None),
                               ('$', None, None, None)
                              ])

        # Two comments with spaces (two lines).
        source = ' // a comment 1 \n // a comment 2 \n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst, [('comment', ' a comment 1 ', ' // a comment 1 \n', None),
                               ('comment', ' a comment 2 ', ' // a comment 2 \n', None),
                               ('$', None, None, None)
                              ])

        #---------------------------------------------------------------
        # C comments, i.e. /* ... */
        #
        # The shortest unclosed comment till the end of data (error).
        source = '/*'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)   # one error item plus endofdata
        self.assertEqual(lst, [('error', "'<str>', 1: '*/' expected",
                                 "('comment', '', '/*', None)", None),
                               ('$', None, None, None)
                              ])

        # The shortest comment (empty) till the end of data.
        source = '/**/'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', '', source, None),
                               ('$', None, None, None)
                              ])

        # Empty comment till the end of line (newline).
        source = '/**/\n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst, [('comment', '', '/**/', None),
                               ('newline', '', '\n', None),
                               ('$', None, None, None)
                              ])

        # Empty comment till the end of line -- newline and space.
        source = '/**/\n '
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst, [('comment', '', '/**/', None),
                               ('newline', '', '\n', None),
                               ('$', None, ' ', None)
                              ])

        # Empty comment till the end of line -- space and newline.
        source = '/**/ \n'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst, [('comment', '', '/**/', None),
                               ('newline', '', ' \n', None),
                               ('$', None, None, None)
                              ])

        # Non-empty comment with spaces.
        source = ' /* a comment */'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', ' a comment ', source, None),
                               ('$', None, None, None)
                              ])

        # A comment with spaces -- three lines.
        source = ' /* a comment 1 \n    a comment 2 \n */'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', ' a comment 1 \n    a comment 2 \n ',
                                source, None),
                               ('$', None, None, None)
                              ])

        # A comment with extra stars.
        source = '/*** a comment ***/'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', '** a comment **', source, None),
                               ('$', None, None, None)
                              ])

        # A comment with stars inside (separated from open/close sequences.
        source = '/* * * a comment * * */'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('comment', ' * * a comment * * ', source, None),
                               ('$', None, None, None)
                              ])


    def test_keywords(self):
        """Catch identifiers considered keywords.
        """
        # Keywords as exact strings with the exact case.
        lst = list(tlex.Container('SCENARIO'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('scenario', None, 'SCENARIO', None),
                               ('$', None, None, None)
                              ])

        lst = list(tlex.Container('GIVEN'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('given', None, 'GIVEN', None),
                               ('$', None, None, None)
                              ])

        lst = list(tlex.Container('WHEN'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('when', None, 'WHEN', None),
                               ('$', None, None, None)
                              ])

        lst = list(tlex.Container('THEN'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('then', None, 'THEN', None),
                               ('$', None, None, None)
                              ])

        lst = list(tlex.Container('TEST_CASE'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('test_case', None, 'TEST_CASE',None),
                               ('$', None, None, None)
                              ])

        lst = list(tlex.Container('SECTION'))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('section', None, 'SECTION', None),
                               ('$', None, None, None)
                              ])

        # Keyword with spaces around.
        lst = list(tlex.Container(' SCENARIO '))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('scenario', None, ' SCENARIO', None),
                               ('$', None, ' ', None)
                              ])


    def test_string_literals(self):
        """recognizing string literals

        String literals are considered test/section identifiers for Catch.
        """
        # Empty string literal.
        source = '""'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', '', '""', None),
                               ('$', None, None, None)
                              ])

        # Simple string literal.
        source = '"simple"'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', 'simple', source, None),
                               ('$', None, None, None)
                              ])

        source = '"words and spaces"'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', 'words and spaces', source, None),
                               ('$', None, None, None)
                              ])

        # Escaped double quote.
        source = r'"\""'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', r'\"', source, None),
                               ('$', None, None, None)
                              ])

        # Escaped tab.
        source = r'"\t"'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', r'\t', source, None),
                               ('$', None, None, None)
                              ])

        # Escaped newline.
        source = r'"\n"'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('stringlit', r'\n', source, None),
                               ('$', None, None, None)
                              ])

        # Not closed literal.
        source = r'"not closed'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('error', '\'<str>\', 1: \'"\' expected',
                  "('stringlit', 'not closed', '\"not closed', None)", None),
                               ('$', None, None, None)
                              ])


    def test_terminals1(self):
        """recognizing one-char terminal symbols
        """
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

        source = ':'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('colon', None, source, None) )

        source = ';'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('semic', None, source, None) )

        source = '='
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('assignment', None, source, None) )


    def test_terminals2(self):
        """recognizing two-char terminal symbols
        """
        source = '=='
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('eq', None, source, None) )


    def test_numbers(self):
        """recognizing number literals
        """
        source = '1'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('num', '1', source, None) )

        source = '12'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('num', '12', source, None) )

        source = '1234567890'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('num', '1234567890', source, None) )


    def test_preprocessor_directive(self):
        """recognizing preprocessor directives
        """
        source = '#endif'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('preprocessor_directive', source, source, None) )

        source = textwrap.dedent('''\
            #define MACRO(arg) \\
                if (arg == "xyz") \\
                    return;
            ''')
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        item = lst[0]
        self.assertEqual(item, ('preprocessor_directive', source, source, None) )


    def test_simple_testcase_and_sections(self):
        """recognizing simple sections with empty body (lexical)
        """
        source = 'TEST_CASE("identifier"){}'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 7)
        self.assertEqual(lst, [('test_case', None, 'TEST_CASE', None),
                               ('lpar', None, '(', None),
                               ('stringlit', 'identifier', '"identifier"', None),
                               ('rpar', None, ')', None),
                               ('lbrace', None, '{', None),
                               ('rbrace', None, '}', None),
                               ('$', None, None, None)
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
                               ('$', None, None, None)
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
                               ('$', None, None, None)
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
                               ('$', None, None, None)
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
                               ('$', None, None, None)
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
                               ('$', None, None, None)
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
                               ('$', None, None, None)
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
                               ('$', None, None, None)
                              ])


    def test_story_or_feature(self):
        """story or feature recognition inside the comment
        """
        # Story
        source = '// Story: story identifier'   # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('$', None, None, None)
                              ])

        source = '// Story: story identifier '  # with trailing space
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('$', None, None, None)
                              ])

        source = '// Story: story identifier\n' # with newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('$', None, None, None)
                              ])

        source = '// Story: story identifier \n' # with trailing space and newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('$', None, None, None)
                              ])

        # Feature
        source = '// Feature: feature identifier'   # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'feature identifier', source, None),
                               ('$', None, None, None)
                              ])

        source = '// Feature: feature identifier\n' # with newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'feature identifier', source, None),
                               ('$', None, None, None)
                              ])

        source = '// Feature: feature identifier \n' # with trailing space and newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'feature identifier', source, None),
                               ('$', None, None, None)
                              ])

        # UsEr StOrY
        source = '// UsEr StOrY: story identifier'      # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('$', None, None, None)
                              ])

        source = '// UsEr StOrY: story identifier\n'    # with newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('$', None, None, None)
                              ])

        # Czech equivalents.
        source = '// PoŽadavek: identifikace požadavku' # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'identifikace požadavku', source, None),
                               ('$', None, None, None)
                              ])

        source = '// rys: identifikace rysu'            # without newline
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'identifikace rysu', source, None),
                               ('$', None, None, None)
                              ])


        # C-comment.
        source = '/* Story: story identifier */'        # single line
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('$', None, None, None)
                              ])


        # Multiline C-comment.
        source = '/*\n Story: story identifier \n  comment2 \n comment3 \n*/'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('story', 'story identifier', source, None),
                               ('$', None, None, None)
                              ])

        source = '/*\n Feature: feature identifier \n  comment2 \n comment3 \n*/'
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [('feature', 'feature identifier', source, None),
                               ('$', None, None, None)
                              ])

    def test_scenario_with_cpp_body_inside_the_body(self):
        """Body of the scenario in {} can contain nested {} not from Catch constructs.
        """
        source = textwrap.dedent('''\
            SCENARIO( "scenario identifier" ) {
                for (int i: container) {
                    do_some_code();
                }
                {}
                {{}}
                {{{}}}
            }''')
        lst = list(tlex.Container(source))
        self.assertEqual(len(lst), 39)

        self.assertEqual(lst, [
            ('scenario', None, 'SCENARIO', None),
            ('lpar', None, '(', None),
            ('stringlit', 'scenario identifier', ' "scenario identifier"', None),
            ('rpar', None, ' )', None),
            ('lbrace', None, ' {', None),
            ('newline', '', '\n', None),
            ('identifier', 'for', '    for', None),
            ('lpar', None, ' (', None),
            ('identifier', 'int', 'int', None),
            ('identifier', 'i', ' i', None),
            ('colon', None, ':', None),
            ('identifier', 'container', ' container', None),
            ('rpar', None, ')', None),
            ('lbrace', None, ' {', None),
            ('newline', '', '\n', None),
            ('identifier', 'do_some_code', '        do_some_code', None),
            ('lpar', None, '(', None),
            ('rpar', None, ')', None),
            ('semic', None, ';', None),
            ('newline', '', '\n', None),
            ('rbrace', None, '    }', None),
            ('newline', '', '\n', None),
            ('lbrace', None, '    {', None),
            ('rbrace', None, '}', None),
            ('newline', '', '\n', None),
            ('lbrace', None, '    {', None),
            ('lbrace', None, '{', None),
            ('rbrace', None, '}', None),
            ('rbrace', None, '}', None),
            ('newline', '', '\n', None),
            ('lbrace', None, '    {', None),
            ('lbrace', None, '{', None),
            ('lbrace', None, '{', None),
            ('rbrace', None, '}', None),
            ('rbrace', None, '}', None),
            ('rbrace', None, '}', None),
            ('newline', '', '\n', None),
            ('rbrace', None, '}', None),
            ('$', None, None, None)
        ])


if __name__ == '__main__':
    unittest.main()