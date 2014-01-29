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
        self.value = None
        self.lexem = None
        self.lexextra_info = None

        self.it = iter(tlex.Container(self.source))
        self.syntax_tree = []   # syntax tree as the list of tuples with lists...
        self.lex()              # prepare the very first token


    def tree(self):
        return self.syntax_tree


    def lex(self):
        '''Get the next lexical token.'''
        try:
            self.lextoken = next(self.it)
            self.sym, self.value, self.lexem, self.lexextra_info = self.lextoken
        except StopIteration:
            pass


    def expect(self, *expected_symbols):
        '''Checks the symbol and gets the next one or reports error.'''
        if self.sym in expected_symbols:
            self.lex()
        else:
            msg = 'Expected symbol(s): {}\n'.format(expected_symbols)
            msg += 'Unexpected symbol: {!r}, {!r}\n'.format(self.sym,
                                                            self.lextoken)
            raise RuntimeError(msg)


    def Start(self):
        '''Implements the start nonterminal.'''

        self.Feature_or_story()
        self.Test_case_serie()
        self.expect('endofdata')


    def Feature_or_story(self):
        '''Nonterminal for processing the story/feature inside comment tokens.'''

        if self.sym == 'story':
            self.syntax_tree.append( (self.sym, self.value) )
            self.lex()
            comment_lst = self.Comments([])
            if comment_lst:
                self.syntax_tree.append( ('storybody', '\n'.join(comment_lst)) )

        elif self.sym == 'feature':
            self.lex()
            comment_lst = self.Comments([])
            if comment_lst:
                self.syntax_tree.append( ('featurebody', '\n'.join(comment_lst)) )

        elif self.sym == 'comment':
            self.lex()
            self.Comments([])   # ignore the other comments

        elif self.sym == 'endofdata':
            pass                # that's OK, the source can be empty
        else:
            self.expect('story', 'feature', 'comment', 'endofdata')


    def Comments(self, comment_lst):
        '''Nonterminal for collecting the content of comments.'''

        if self.sym == 'comment':
            comment_lst.append(self.value)
            self.lex()
            return self.Comments(comment_lst)
        else:
            return comment_lst


    def Test_case_serie(self):
        '''Nonterminal for a serie of test cases or scenarios.'''

        if self.sym in ('scenario', 'test_case'):
            t = self.Test_case()
            self.syntax_tree.append(t)
            self.Test_case_serie()

        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the test cases.
            self.lex()
            self.Test_case_serie()
        elif self.sym == 'endofdata':
            pass        # that's OK, no test_source or scenario is acceptable
        else:
            self.expect('scenario', 'test_case', 'emptyline', 'endofdata')


    def Test_case(self):
        '''Nonterminal for one TEST_CASE or one SCENARIO.'''

        item = [ self.sym ]      # specific symbol: 'test_case' or 'scenario'
        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            item.append(self.value)
            self.lex()
        else:
            self.expect('stringlit')

        # Optional argument with tags.
        if self.sym == 'comma':
            self.lex()
            if self.sym == 'stringlit':
                raise NotImplementedError('syntax tree for tags not implemented')
                self.lex()
            else:
                expect('stringlit')
        self.expect('rpar')
        self.expect('lbrace')

        # Collect the subree of the test_case body.
        subtree = self.Code_body([])
        self.expect('rbrace')

        # Return the collected symbol, identifier, and body the test_case into the syntaxt tree.
        item.append(subtree)
        return tuple(item)


    def Code_body(self, subtree):
        '''Nonterminal for any other code between the {}.'''

        if self.sym == 'rbrace':
            return subtree      # empty rule
        elif self.sym in ('section', 'given', 'when', 'then'):
            secitem = self.Section()
            subtree.append(secitem)

        self.lex()
        return self.Code_body(subtree)


    def Section(self):
        '''Nonterminal for SECTION, GIVEN, WHEN, ...'''

        item = [ self.sym ]      # specific symbol
        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            item.append(self.value)
            self.lex()
        else:
            self.expect('stringlit')

        self.expect('rpar')
        self.expect('lbrace')

        # Collect the subree of the test_case body.
        subtree = self.Code_body([])
        self.expect('rbrace')

        # Output the previously collected symbol, identifier, and body
        # of the section into the syntaxt tree.
        item.append(subtree)
        return tuple(item)


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
        ''')

    sa = SyntacticAnalyzerForCatch(source)
    sa.Start()          # run from the start nonterminal
    print(sa.tree())