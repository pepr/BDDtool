#!python3
# -*- coding: utf-8 -*-
'''Syntactic analysis for the *.feature files.'''

import felex
import re
import sys
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


    def lex(self):
        '''Get the next lexical token.'''
        try:
            self.lextoken = next(self.it)
            self.sym, self.text, self.lexem, self.tags = self.lextoken
        except StopIteration:
            pass


    def expect(self, *expected_symbols):
        '''Checks the symbol and gets the next one or reports error.'''
        if self.sym in expected_symbols:
            self.lex()
        else:
            print('Expected symbol(s):', expected_symbols)
            print('Unexpected symbol: {!r}, {!r}'.format(self.sym,
                                                         self.lextoken))
            sys.exit()


    def Start(self):
        '''Implements the start nonterminal.'''

        self.Feature_or_story()
        self.Test_or_scenario_serie()
        self.expect('endofdata')


    def Feature_or_story(self):
        '''Nonterminal for processing the story/feature definition.'''

        if self.sym == 'story':
            print('Story:', self.text)
            self.lex()
            self.Description()
        elif self.sym == 'feature':
            print('Feature:', self.text)
            self.Description()
        else:
            self.expect('story', 'feature')


    def Description(self):
        '''Nonterminal for description lines of the story/feature.'''

        if self.sym in ('emptyline', 'line'):
            print(self.text)
            self.lex()
            self.Description()


    def Test_or_scenario_serie(self):
        '''Nonterminal for a serie of test-case or scenario definitions.'''

        if self.sym == 'test_case':
            self.Test_case()
            self.Test_or_scenario_serie()
        elif self.sym == 'scenario':
            self.Scenario()
            self.Test_or_scenario_serie()
        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the test cases.
            self.lex()
            self.Test_or_scenario_serie()
        elif self.sym == 'endofdata':
            # No test-case nor scenario in the feature definition.
            return
        else:
            self.expect('test_case', 'scenario')


    def Test_case(self):
        '''Nonterminal for one TEST_CASE.'''

        print('Test:', self.text)
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

        print('Scenario:', self.text)
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