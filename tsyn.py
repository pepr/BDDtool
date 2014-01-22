#!python3
# -*- coding: utf-8 -*-
'''Syntactic analysis for the Catch test sources.'''

import re
import sys
import tlex
import textwrap

class SyntacticAnalyzerForCatch:

    def __init__(self, source):
        self.source = source

        self.lextoken = None
        self.sym = None

        self.it = iter(tlex.Container(self.source))
        self.info_lst = []      # auxiliary list for extracted info
        self.comment_lines = [] # list for lines extracted from comment blocks
        self.syntax_root = []   # root node of the syntax tree
        self.bodylst = []       # lines of the story/feature description
        self.testcaselst = []   # test case subtrees


    def lex(self):
        '''Get the next lexical token.'''
        try:
            self.lextoken = next(self.it)
            self.sym = self.lextoken[0]
        except StopIteration:
            pass


    def unexpected(self):
        print('Unexpected symbol: {!r}, {!r}'.format(self.sym, self.lextoken))
        sys.exit()


    def clear_output(self):
        self.info_lst = []


    def output_is_empty(self):
        return len(self.info_lst) == 0


    def out(self, s):
        self.info_lst.append(s)


    def output_as_string(self, joinseparator=''):
        return joinseparator.join(self.info_lst)



    def expect(self, *expected_symbols):
        '''Checks the symbol and gets the next one or reports error.'''
        if self.sym in expected_symbols:
            self.lex()
        else:
            print('Expected symbol(s):', expected_symbols)
            self.unexpected()


    def Start(self):
        '''Implements the start nonterminal.'''

        self.Feature_or_story()
        self.Test_case_serie()
        self.expect('endofdata')


    def Feature_or_story(self):
        '''Nonterminal for processing the story/feature inside comment tokens.'''

        if self.sym == 'story':
            print('Story:', self.lextoken[1])
            self.lex()
            self.Comments()
        elif self.sym == 'feature':
            print('Story:', self.lextoken[1])
            self.Comments()
        elif self.sym == 'comment':
            print(self.lextoken[1])
            self.Comments()
        else:
            self.expect('story', 'feature', 'comment')


    def Comments(self):
        '''Nonterminal for skipping the block of comments.'''

        if self.sym == 'comment':
            print(self.lextoken[1])
            self.lex()
            self.Comments()


    def Test_case_serie(self):
        '''Nonterminal for a serie of test cases or scenarios.'''

        if self.sym in ('scenario', 'test_case'):
            self.Test_case(self.sym)
        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the test cases.
            self.lex()
            self.Test_case_serie()
        elif self.sym == 'endofdata':
            return
        else:
            self.unexpected()


    def Test_case(self, variant):
        '''Nonterminal for one TEST_CASE or one SCENARIO.'''

        self.out('\n{}: '.format(variant))
        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            self.out(self.lextoken[1])
            self.lex()
        else:
            self.expect('stringlit')

        # Optional argument with tags.
        if self.sym == 'comma':
            self.lex()
            if self.sym == 'stringlit':
                self.out('  ' + self.lextoken[1])
                self.lex()
            else:
                expect('stringlit')
        self.expect('rpar')
        self.expect('lbrace')

        # Output the previously collected result. It is because
        # the following body contains sections, and they in turn
        # other sections. All of them must be reported in the order.
        print(self.output_as_string())
        self.clear_output()

        self.Code_body()
        self.expect('rbrace')
        self.Test_case_serie()


    def Code_body(self):
        '''Nonterminal for any other code between the {}.'''

        if self.sym == 'rbrace':
            return              # empty rule
        elif self.sym in ('section', 'given', 'when', 'then'):
            self.Section(self.sym)

        self.lex()
        self.Code_body()


    def Section(self, variant):
        '''Nonterminal for SECTION, GIVEN, WHEN, ...'''

        self.out('  {}: '.format(variant))
        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            self.out(self.lextoken[1])
            self.lex()
        else:
            self.expect('stringlit')

        self.expect('rpar')
        self.expect('lbrace')

        # Output the previously collected result. It is because
        # the following body contains sections...
        print(self.output_as_string())
        self.clear_output()

        self.Code_body()
        self.expect('rbrace')


#-----------------------------------------------------------------------

if __name__ == '__main__':
    source = textwrap.dedent('''\
        // Story: story identifier
        //
        //  As a user
        //  I want the feature
        //  so that my life is to be easier.

        SCENARIO( "scenario 1 identifier" ) {
        }
        SCENARIO( "scenario 2 identifier" ) {
        }
        TEST_CASE( "test case 1 identifier" ) {
        }
        TEST_CASE( "test case 2 identifier" ) {
        }
        SCENARIO( "scenario identifier" ) {
            GIVEN( "given identifier" ) {
                // set up initial state

                WHEN( "when identifier" ) {
                    // perform operation

                    THEN( "then identifier" ) {
                        // assert expected state
                    }
                }
            }
        }
        SCENARIO( "name for scenario", "[optional tags]" ) {
            GIVEN( "some initial state" ) {
                // set up initial state

                WHEN( "an operation is performed" ) {
                    // perform operation

                    THEN( "we arrive at some expected state" ) {
                        // assert expected state
                    }
                }
            }
        }
        ''')

    sa = SyntacticAnalyzerForCatch(source)
    sa.lex()            # prepare the first lexical token
    sa.Start()          # run from the start nonterminal