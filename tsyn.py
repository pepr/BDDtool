#!python3
"""Syntactic analysis for the Catch test sources.

The methods of the SyntacticAnalyzerForCatch class that start with
a capital letter do implement recursive parsing of the related nonterminal.
"""

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


    def lex(self):
        """Get the next lexical token.
        """
        try:
            self.lextoken = next(self.it)
            self.sym, self.value, self.lexem, self.lexextra_info = self.lextoken
        except StopIteration:
            pass


    def expect(self, *expected_symbols):
        """Checks the symbol and gets the next one or reports error.
        """
        if self.sym in expected_symbols:
            self.lex()
        else:
            msg = 'Expected symbol(s): {}\n'.format(expected_symbols)
            msg += 'Unexpected symbol: {!r}, {!r}\n'.format(self.sym,
                                                            self.lextoken)
            raise RuntimeError(msg)


    #-------------------------------------------------------------------------
    def Start(self):
        """Implements the start nonterminal.
        """
        self.Feature_or_story()
        self.Test_case_or_scenario_serie()
        self.expect('$')
        return self.syntax_tree


    def Other_lines(self):
        """Nonterminal for the sequence of zero or more 'emptyline' or 'line' tokens.
        """
        if self.sym in ('emptyline', 'code'):
            self.lex()
            self.Other_lines()

    #-------------------------------------------------------------------------
    def Feature_or_story(self):
        """Nonterminal for processing the story/feature inside comment tokens.
        """
        self.Other_lines()
        if self.sym in ('story', 'feature'):
            self.syntax_tree.append( (self.sym, self.value) )
            self.lex()
            comment_lst = []
            self.Comments(comment_lst)
            if comment_lst:
                self.syntax_tree.append( ('description', comment_lst) )
        elif self.sym == '$':
            pass                # that's OK, the source can be empty
        else:
            self.expect('story', 'feature', '$')


    def Comments(self, comment_lst):
        """Nonterminal for collecting the content of comments.
        """
        if self.sym == 'comment':
            comment_lst.append(self.value)
            self.lex()
            self.Comments(comment_lst)


    def Test_case_or_scenario_serie(self):
        """Nonterminal for a serie of test cases or scenarios.
        """
        self.Other_lines()
        if self.sym == 'test_case':
            self.Test_case()
            self.Test_case_or_scenario_serie()
        elif self.sym == 'scenario':
            self.Scenario()
            self.Test_case_or_scenario_serie()


    #-------------------------------------------------------------------------
    def Test_case(self):
        """Nonterminal for one TEST_CASE.
        """
        assert self.sym == 'test_case'
        item = [self.sym]               # first element of the item = symbol

        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            item.append(self.value)     # second element = test identification
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
        bodylst = []
        self.Section_serie(bodylst)
        self.expect('rbrace')

        # Append the collected test case item to the syntax tree.
        item.append(bodylst)            # third element of the item = subtree
        self.syntax_tree.append(tuple(item))


    def Section_serie(self, upperlst):
        """Nonterminal for any other code between the {}.
        """
        self.Other_lines()
        elif self.sym == 'section':
            self.Section(upperlst)
            self.Other_lines()
            self.Section_serie(upperlst)


    def Section(self, upperlst):
        """Nonterminal for SECTION
        """
        assert self.sym == 'section'
        item = [self.sym]               # first element with the symbol
        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            item.append(self.value)     # second element with the value
            self.lex()
        else:
            self.expect('stringlit')

        self.expect('rpar')
        self.expect('lbrace')

        bodylst = []
        item.append(bodylst)            # third element with the subtree

        # Simplified implementation. The sections are not expected to be nested.
        # Just skip the other lines.
        self.Other_lines()
        self.expect('rbrace')

        # Output the previously collected symbol, identifier, and body
        # of the section into the syntaxt tree.
        upperlst.append(tuple(item))

    #-------------------------------------------------------------------------
    def Scenario(self):
        """Nonterminal for one SCENARIO.
        """
        assert self.sym == 'scenario'
        item = [self.sym]               # first element with the symbol
        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            item.append(self.value)     # second element with the value
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

        bodylst = []
        item.append(bodylst)            # third element with the subtree

        # Append the scenario item to the syntax tree. The bodylst will be
        # filled later.
        self.syntax_tree.append(tuple(item))

        # Skip the other lines -- 'given' expected.
        self.Other_lines()
        if self.sym == 'given':
            self.Given_serie(bodylst)

        self.expect('rbrace')

    #-------------------------------------------------------------------------
    def Given_serie(self, upperlst):
        """Zero or more GIVEN items (at the same level).
        """
        self.Other_lines()      # neccessary for the recursion
        if self.sym == 'given':
            self.Given(upperlst)
            self.Given_serie(upperlst)


    def Given(self, upperlst):
        """Nonterminal for one GIVEN definition.
        """
        assert self.sym == 'given'
        item = [self.sym]               # first element with the symbol
        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            item.append(self.value)     # second element with the value
            self.lex()
        else:
            self.expect('stringlit')

        self.expect('rpar')
        self.expect('lbrace')

        bodylst = []
        item.append(bodylst)            # third element with the subtree

        # Append the item to the upperlst. The bodylst will be filled by
        # the syntax subtree later.
        upperlst.append(tuple(item))

        # Skip the other lines, and process the nested items.
        self.Other_lines()
        if self.sym == 'when':
            self.When_serie(bodylst)    # nested to the given
        elif self.sym == 'given':
            self.sym = 'and_given'      # symbol transformation
            self.And_given(bodylst)     # nested to the given

        self.expect('rbrace')


???    def And_given(self, upperlst):
        """Nonterminal for one AND_GIVEN definition.
        """
        assert self.sym == 'and_given'
        bodylst = []                            # body of the given item
        item = [self.sym, self.text, bodylst]   # 'and_given', 'id', body
        upperlst.append(tuple(item))            # ready to be appended

        self.lex()
        self.Empty_lines()
        if self.sym == 'when':
            self.When(bodylst)          # nested to the given
        elif self.sym == 'and':
            self.sym = 'and_given'      # symbol transformation
            self.And_given(bodylst)     # nested to the given


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