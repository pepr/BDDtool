#!python3
# -*- coding: utf-8 -*-
'''Syntactic analysis for the Catch test sources.'''

import re
import sys
import tlex
import textwrap

class SyntacticAnalyzerForCatch:

    # Regular expressions for recognizing the Feature/Story lines.
    rexStory = re.compile(r'''\s*
                              ((User\s+)?Story
                               |(Uživatelský\s+)?Požadavek
                               |Feature
                               |Rys
                              )
                              :''', re.VERBOSE | re.IGNORECASE)

    rexFeature = re.compile(r'''\s*
                              (Feature
                               |Rys
                              )
                              :''', re.VERBOSE | re.IGNORECASE)


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
        ##print(self.lextoken)
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

        self.syntax_tree = []   # no childrend for the root node, yet

        lst = self.Feature_or_story_comments()
        self.syntax_tree.extend(lst)

        lst = self.Test_case_serie()
        self.syntax_tree.extend(lst)

        self.expect('endofdata')


    def Feature_or_story_comments(self):
        '''Nonterminal for processing the story/feature inside comment tokens.'''

        subtree = []    # syntax subtree node with no children, yet

        if self.sym == 'comment':
            m = self.rexStory.match(self.lextoken[1])
            if m is not None:
                # Extract the Story identifier.
                storyid = self.lextoken[1][m.endpos:]
                subtree.append( ('story', storyid) )
            else:
                m = self.rexFeature.match(self.lextoken[1])
                if m is not None:
                    # Extract the Story identifier.
                    featureid = self.lextoken[1][m.endpos:]
                    subtree.append( ('feature', featureid) )
                else:
                    self.expect('story or feature')

            body = self.Feature_or_story_text()
            subtree.append(body)

        return subtree

#        # The same info can be part of more single-line comments (// ...) or one
#        # multi-line comments (/* ... */). To unify their processing, the comment
#        # block is firstly converted to the list of lines constructed from
#        # the comment lines.
#        self.comment_lines = []
#        while self.sym == 'comment':
#            if self.lextoken[2].endswith('//'):
#                self.comment_lines.append(self.lextoken[1]) # a // C++ comment
#            else:
#                self.comment_lines.extend(self.lextoken[1].split('\n'))
#            self.lex()
#
#        if self.comment_lines:          # if there are any comment lines
#            self.Feature_or_story_comments_from_list()
#        else:
#            # Produce the collected result.
#            print(self.output_as_string())
#            self.clear_output()


    def Feature_or_story_text(self):
        '''Nonterminal for processing the story/feature description text.'''

        if self.sym == 'comment':
            self.bodylst.append(self.lextoken[1].strip())
            self.lex()
            self.Feature_or_story_text()

        body = '\n'.join(self.bodylst)
        self.bodylst = []
        return body


    def Test_case_serie(self):

        if self.sym in ('scenario', 'test_case'):
            subtree = self.Test_case(self.sym)
            self.testcaselst.append(subtree)
        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the test cases.
            self.lex()
            tclist = self.Test_case_serie()
            self.testcaselst.extend(tclist)

        elif self.sym == 'endofdata':
            return
        else:
            self.unexpected()

        return []  ##??? fake


    def Test_case(self, variant):
        '''Nonterminal for TEST_CASE or SCENARIO.'''

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
        lst = self.Test_case_serie()
        return [].extend(lst)  ##??? fake


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