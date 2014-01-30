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

        elif self.sym in ('endofdata', 'scenario', 'test_case'):
            pass # empty source, or no story definition, nor feature def
        else:
            self.expect('story', 'feature', 'endofdata', 'scenario', 'test_case')


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

        item = [ self.sym, self.text ]          # specific symbol: 'test_case'
        self.lex()
        if self.sym == 'section':
            sec_lst = self.Section_serie([])
            item.append(sec_lst)
            return tuple(item)

        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the SECTION.
            self.lex()
            sec_lst = self.Section_serie([])
            item.append(sec_lst)
            return tuple(item)

        elif self.sym == 'endofdata':
            # Empty body of the test_case (that is no section).
            item.append([])
            return tuple(item)
        else:
            self.expect('section', 'emptyline', 'endofdata')


    def Scenario(self):
        '''Nonterminal for one Scenario.'''

        item = [ self.sym, self.text ]          # specific symbol: 'scenario'
        self.lex()
        if self.sym == 'given':
            given_lst = self.Given_serie([])
            item.append(given_lst)
            return tuple(item)

        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the GIVEN.
            self.lex()
            given_lst = self.Given_serie([])
            item.append(given_lst)
            return tuple(item)

        elif self.sym == 'endofdata':
            # Empty body of the scenario (that is no given...).
            item.append([])
            return tuple(item)
        else:
            self.expect('given', 'emptyline', 'endofdata')


    def Given_serie(self, given_lst):
        '''Nonterminal for a serie of GIVEN definitions.'''

        if self.sym == 'given':
            t = self.Given()
            given_lst.append(t)
            return self.Given_serie(given_lst)

        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the GIVEN.
            self.lex()
            return self.Given_serie(given_lst)

        elif self.sym == 'endofdata':
            # No more GIVENs.
            return given_lst
        else:
            self.expect('given', 'emptyline', 'endofdata')


    def Given(self):
        '''Nonterminal for one GIVEN definition.'''

        item = [ self.sym, self.text ]          # 'given', 'identifier'
        self.lex()
        if self.sym == 'when':
            when_lst = self.When_serie([])
            item.append(when_lst)
            return tuple(item)

        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the WHEN.
            self.lex()
            when_lst = self.When_serie([])
            item.append(when_lst)
            return tuple(item)

        elif self.sym == 'endofdata':
            # No more WHENs.
            return when_lst
        else:
            self.expect('when', 'emptyline', 'endofdata')


    def When_serie(self, when_lst):
        '''Nonterminal for a serie of WHEN definitions.'''

        if self.sym == 'when':
            t = self.When()
            when_lst.append(t)
            return self.When_serie(when_lst)

        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the WHEN.
            self.lex()
            return self.When_serie(when_lst)

        elif self.sym == 'endofdata':
            # No more WHENs.
            return when_lst
        else:
            self.expect('when', 'emptyline', 'endofdata')


    def When(self):
        '''Nonterminal for one WHEN definition.'''

        item = [ self.sym, self.text ]          # 'when', 'identifier'
        self.lex()
        if self.sym == 'then':
            t = self.Then()
            item.append( [ t ])                 # as a body of 'when'
            return tuple(item)
        else:
            self.expect('then')


    def Then(self):
        '''Nonterminal for one THEN definition.'''

        item = [ self.sym, self.text ]          # 'then', 'identifier'
        self.lex()
        item.append([]) # no more nesting
        return tuple(item)



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
    tree = sa.Start()   # run from the start nonterminal
    print(tree)