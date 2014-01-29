#!python3
# -*- coding: utf-8 -*-
'''Syntactic analysis for the *.feature files.'''

import felex
import re
import textwrap


class SyntacticAnalyzerForFeature:

    def __init__(self, source):
        self.source = source

        self.lextoken = None    # ... extracted to
        self.sym   = None       # symbol
        self.text  = None       # value
        self.lexem = None       # lexem
        self.tags  = None       # extra_info

        self.it = iter(felex.Container(self.source))
        self.lex()              # getting the first token ready
        self.syntax_tree = []   # syntax tree as the list of tuples with lists...


    def lex(self):
        '''Get the next lexical token.'''
        try:
            self.lextoken = next(self.it)
            ##print(self.lextoken)
            self.sym, self.text, self.lexem, self.tags = self.lextoken
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

        return self.syntax_tree


    def Feature_or_story(self):
        '''Nonterminal for processing the story/feature definition.'''

        if self.sym in ('story', 'feature'):
            self.syntax_tree.append( (self.sym, self.text) )
            self.lex()
            descr_lst = self.Description([])
            if descr_lst:
                self.syntax_tree.append( ('description', '\n'.join(descr_lst)) )

        elif self.sym == 'endofdata':
            pass                # that's OK, the source can be empty
        else:
            self.expect('story', 'feature', 'endofdata')


    def Description(self, descr_lst):
        '''Nonterminal for description lines of the story/feature.'''

        if self.sym in ('emptyline', 'line'):
            descr_lst.append(self.text)
            self.lex()
            return self.Description(descr_lst)
        else:
            return descr_lst


    def Test_case_serie(self):
        '''Nonterminal for a serie of test-case or scenario definitions.'''

        if self.sym == 'test_case':
            t = self.Test_case()
            self.syntax_tree.append(t)
            self.Test_case_serie()
        elif self.sym == 'scenario':
            t = self.Scenario()
            self.syntax_tree.append(t)
            self.Test_case_serie()
        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the test cases.
            self.lex()
            self.Test_case_serie()
        elif self.sym == 'endofdata':
            pass        # that's OK, no test_source or scenario is acceptable
        else:
            self.expect('test_case', 'scenario')


    def Test_case(self):
        '''Nonterminal for one TEST_CASE.'''

        item = [ self.sym ]      # specific symbol: 'test_case'
        self.lex()
        if self.sym == 'section':
            self.Section_serie()
        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the SECTION.
            self.lex()
            self.Section_serie()
        else:
            self.expect('section')


    def Scenario(self):
        '''Nonterminal for one Scenario.'''

        item = [ self.sym ]      # specific symbol: 'scenario'
        self.lex()
        if self.sym == 'given':
            self.Given_serie()
        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the GIVEN.
            self.lex()
            self.Given_serie()
        elif self.sym == 'endofdata':
            return
        else:
            self.expect('given')


    def Given_serie(self):
        '''Nonterminal for a serie of GIVEN definitions.'''

        if self.sym == 'given':
            self.Given()
            self.Given_serie()
        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the GIVEN.
            self.lex()
            self.Given_serie()
        elif self.sym == 'endofdata':
            # No more GIVENs.
            return
        else:
            self.expect('given')


    def Given(self):
        '''Nonterminal for one GIVEN definition.'''

        print('   Given:', self.text)
        self.lex()
        if self.sym == 'when':
            self.When_serie()
        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the WHEN.
            self.lex()
            self.When_serie()
        else:
            self.expect('when')


    def When_serie(self):
        '''Nonterminal for a serie of WHEN definitions.'''

        if self.sym == 'when':
            self.When()
            self.When_serie()
        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the WHEN.
            self.lex()
            self.When_serie()
        elif self.sym == 'endofdata':
            # No more WHENs.
            return
        else:
            self.expect('when')


    def When(self):
        '''Nonterminal for one WHEN definition.'''

        print('    When:', self.text)
        self.lex()
        if self.sym == 'then':
            self.Then_serie()
        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the THEN.
            self.lex()
            self.Then_serie()
        else:
            self.expect('then')



    def Then_serie(self):
        '''Nonterminal for a serie of THEN definitions.'''

        if self.sym == 'then':
            self.Then()
            self.Then_serie()
        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the THEN.
            self.lex()
            self.Then_serie()
        elif self.sym == 'endofdata':
            # No more THENs.
            return
        else:
            self.expect('then')


    def Then(self):
        '''Nonterminal for one THEN definition.'''

        print('    Then:', self.text)
        self.expect('then')



#-----------------------------------------------------------------------

if __name__ == '__main__':
    source = textwrap.dedent('''\
        Story: story identifier

          As a user
          I want the feature
          so that my life is to be easier.

        Scenario: scenario identifier
           Given: given identifier
            When: when identifier
            Then: then identifier
        ''')

    sa = SyntacticAnalyzerForFeature(source)
    sa.lex()            # prepare the first lexical token
    sa.Start()          # run from the start nonterminal