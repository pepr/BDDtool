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
            line_no = self.it.lineno
            source_name = self.it.source_name
            msg = 'Expected symbol(s): {}\n'.format(expected_symbols)
            msg += ('Unexpected content in {!r} at line {}:\n'
                    '{!r}, {!r}\n').format(
                        source_name, line_no, self.sym, self.value)
            raise RuntimeError(msg)


    #-------------------------------------------------------------------------
    def Start(self):
        """Implements the start nonterminal.
        """
        self.Feature_or_story()
        self.Test_case_or_scenario_serie()
        self.expect('$')
        return self.syntax_tree


    def Ignored_symbols(self):
        """Nonterminal for the sequence of zero or more 'newline' or 'line' tokens.
        """
        if self.sym in ('comment', 'newline'):
            self.lex()
            self.Ignored_symbols()
        ???    
        elif self.sym in ('comment', 'hash', 'identifier', 'newline',
                        'stringlit', 'semic', 'assignment',
                        'num', 'colon'):
            ## print('Ignored_symbols():', repr(self.sym))
            self.lex()
            self.Ignored_symbols()


    #-------------------------------------------------------------------------
    def Feature_or_story(self):
        """Nonterminal for processing the story/feature inside comment tokens.
        """
        self.Ignored_symbols()
        if self.sym in ('story', 'feature'):
            self.syntax_tree.append( (self.sym, self.value) )
            self.lex()
            comment_lst = []
            self.Comments(comment_lst)
            if comment_lst:
                while comment_lst[0] == '':
                    del comment_lst[0]
                self.syntax_tree.append( ('description', comment_lst) )


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
        self.Ignored_symbols()
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
        item.append(bodylst)            # third element of the item = subtree

        # Append the test case item to the syntax tree. The bodylst will be
        # filled later.
        self.syntax_tree.append(tuple(item))

        # Skip the other lines -- 'section' expected.
        self.Ignored_symbols()
        if self.sym == 'section':
            self.Section_serie(bodylst)
        elif self.sym == 'lbrace':
            self.Block_of_code()

        self.Ignored_symbols()
        self.expect('rbrace')


    def Section_serie(self, upperlst):
        """Nonterminal for any other code between the {}.
        """
        self.Ignored_symbols()
        if self.sym == 'section':
            self.Section(upperlst)
            self.Ignored_symbols()
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
        self.Ignored_symbols()
        self.expect('rbrace')

        # Output the previously collected symbol, identifier, and body
        # of the section into the syntax tree.
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
        self.Ignored_symbols()
        if self.sym == 'given':
            self.Given_serie(bodylst)
        elif self.sym == 'lbrace':
            ## print('block')
            self.Block_of_code()

        self.Ignored_symbols()
        self.expect('rbrace')

    #-------------------------------------------------------------------------
    def Given_serie(self, upperlst):
        """Zero or more GIVEN items (at the same level).
        """
        self.Ignored_symbols()      # necessary for the recursion
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
            item.append(self.value)     # second element with the identifier
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
        self.Ignored_symbols()
        if self.sym == 'when':
            self.When_serie(bodylst)    # nested to the given
        elif self.sym == 'given':
            self.sym = 'and_given'      # symbol transformation
            self.And_given(bodylst)     # nested to the given

        self.Ignored_symbols()
        self.expect('rbrace')


    def And_given(self, upperlst):
        """Nonterminal for one AND_GIVEN definition -- always nested.
        """
        assert self.sym == 'and_given'
        item = [self.sym]               # first element with the symbol
        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            item.append(self.value)     # second element with the identifier
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
        self.Ignored_symbols()
        if self.sym == 'when':
            self.When_serie(bodylst)    # nested to the and_given
        elif self.sym == 'given':       # Catch does not know AND_GIVEN
            self.sym = 'and_given'      # symbol transformation
            self.And_given(bodylst)     # nested to this and_given

        self.Ignored_symbols()
        self.expect('rbrace')


    #-------------------------------------------------------------------------
    def When_serie(self, upperlst):
        """Nonterminal for a serie of WHEN definitions.
        """
        self.Ignored_symbols()              # neccessary for the recursion
        if self.sym == 'when':
            self.When(upperlst)
            self.When_serie(upperlst)


    def When(self, upperlst):
        """Nonterminal for one WHEN definition.
        """
        assert self.sym == 'when'
        item = [self.sym]               # first element with the symbol
        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            item.append(self.value)     # second element with the identifier
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
        self.Ignored_symbols()
        if self.sym == 'then':
            self.Then(bodylst)          # nested
        elif self.sym == 'and_when':
            self.And_when(bodylst)      # nested to this when

        self.Ignored_symbols()
        self.expect('rbrace')


    def And_when(self, upperlst):
        """Nonterminal for one AND_WHEN definition.
        """
        assert self.sym == 'and_when'
        item = [self.sym]               # first element with the symbol
        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            item.append(self.value)     # second element with the identifier
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
        self.Ignored_symbols()
        if self.sym == 'then':
            self.Then(bodylst)          # nested
        elif self.sym == 'and_when':
            self.And_when(bodylst)      # nested to this and_when

        self.Ignored_symbols()
        self.expect('rbrace')


    #-------------------------------------------------------------------------
    def Then(self, upperlst):
        """Nonterminal for one THEN definition.
        """
        assert self.sym == 'then'
        item = [self.sym]               # first element with the symbol
        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            item.append(self.value)     # second element with the identifier
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
        self.Ignored_symbols()
        if self.sym == 'and_then':
            self.And_then(bodylst)      # nested to the previous then-item

        self.Ignored_symbols()
        self.expect('rbrace')


    def And_then(self, upperlst):
        """Nonterminal for one AND_THEN definition.
        """
        assert self.sym == 'and_then'
        item = [self.sym]               # first element with the symbol
        self.lex()
        self.expect('lpar')
        if self.sym == 'stringlit':
            item.append(self.value)     # second element with the identifier
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
        self.Ignored_symbols()
        if self.sym == 'and_then':
            self.And_then(bodylst)      # nested to the previous then-item

        self.Ignored_symbols()
        self.expect('rbrace')

    #-------------------------------------------------------------------------
    def Block_of_code(self):
        """C/C++ block of code in curly braces -- or sequence of block or nested.
        """
        if self.sym == 'lbrace':
            self.expect('lbrace')
            self.Ignored_symbols()
            self.Block_of_code()        # nested
            self.expect('rbrace')
            self.Ignored_symbols()
            self.Block_of_code()        # sequence

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