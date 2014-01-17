#!python3
# -*- coding: utf-8 -*-
'''Syntactic analysis for the Catch test sources.'''

import tlex
import textwrap
import sys

class SyntacticAnalyzerForCatch:


    def __init__(self, source):
        self.source = source

        self.lexlst = []        # processed lex items (i.e. history)

        self.lexitem = None
        self.sym = None

        self.it = iter(tlex.Container(self.source))
        self.info_lst = []      # auxiliary list for extracted info


    def lex(self):
        '''Get the next lexical item.'''
        ##print(self.lexitem)
        try:
            self.lexitem = next(self.it)
            self.sym = self.lexitem[0]
        except StopIteration:
            pass


    def unexpected(self):
        print('Unexpected symbol: {!r}, {!r}'.format(self.sym, self.lexitem))
        sys.exit()


    def clear_info(self):
        self.info_lst = []


    def info_is_empty(self):
        return len(self.info_lst) == 0


    def append_info(self, s):
        self.info_lst.append(s)


    def info_as_string(self, joinseparator=''):
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
        self.Feature_or_story_comments()
        self.Test_case_serie()
        self.expect('endofdata')


    def Feature_or_story_comments(self):
        '''Nonterminal for processing the info inside comment items.'''

        if self.sym == 'comment':

            # Check whether the comment contains the story/feature
            # label. If yes, start collecting the story.
            if 'Story:' in self.lexitem[1] or not self.info_is_empty():
                self.append_info(self.lexitem[1])
            self.lex()  # advance to the next lex item
            self.Feature_or_story_comments()    # extract the next comments
        else:
            # Produce the collected result.
            print(self.info_as_string())
            self.clear_info()


    def Test_case_serie(self):

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
        '''Nonterminal for TEST_CASE or SCENARIO.'''

        self.append_info('\n{}: '.format(variant))
        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            self.append_info(self.lexitem[1])
            self.lex()
        else:
            self.expect('stringlit')

        # Optional argument with tags.
        if self.sym == 'comma':
            self.lex()
            if self.sym == 'stringlit':
                self.append_info('  ' + self.lexitem[1])
                self.lex()
            else:
                expect('stringlit')
        self.expect('rpar')
        self.expect('lbrace')

        # Output the previously collected result. It is because
        # the following body contains sections, and they in turn
        # other sections. All of them must be reported in the order.
        print(self.info_as_string())
        self.clear_info()

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

        self.append_info('  {}: '.format(variant))
        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            self.append_info(self.lexitem[1])
            self.lex()
        else:
            self.expect('stringlit')

        self.expect('rpar')
        self.expect('lbrace')

        # Output the previously collected result. It is because
        # the following body contains sections...
        print(self.info_as_string())
        self.clear_info()

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
    sa.lex()            # prepare the first lexical item
    sa.Start()          # run from the start nonterminal