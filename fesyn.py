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


    def addToBodyOf(self, item, lst):
        '''Adds list of items lst to the item body list.'''
        if item[2] is None:
            item[2] = lst
        else:
            item[2].extend(lst)


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


    def Test_case(self, item=None):
        '''Nonterminal for one TEST_CASE.'''

        if item is None:
            item = [ self.sym, self.text, None ]
        self.lex()
        if self.sym == 'section':
            self.addToBodyOf(item, sec_lst)
            return tuple(item)

        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the SECTION.
            self.lex()
            sec_lst = self.Section_serie([])
            self.addToBodyOf(item, sec_lst)
            return tuple(item)

        elif self.sym == 'endofdata':
            # Empty body of the test_case (that is no section).
            self.addToBodyOf(item, [])
            return tuple(item)
        else:
            self.expect('section', 'emptyline', 'endofdata')


    def Scenario(self):
        '''Nonterminal for one Scenario.'''

        item = [ self.sym, self.text, None ]       # specific symbol: 'scenario'
        self.lex()
        if self.sym == 'given':
            given_lst = self.Given_serie([])
            self.addToBodyOf(item, given_lst)
            return tuple(item)

        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the GIVEN.
            self.lex()
            given_lst = self.Given_serie([])
            self.addToBodyOf(item, given_lst)
            return tuple(item)

        elif self.sym == 'endofdata':
            # Empty body of the scenario (that is no given...).
            self.addToBodyOf(item, [])
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

        elif self.sym == 'scenario':
            # No more GIVENs -- another scenario to be processed.
            return given_lst

        elif self.sym == 'endofdata':
            # No more GIVENs.
            return given_lst
        else:
            self.expect('given', 'emptyline', 'scenario', 'endofdata')


    def Given(self, item=None, restriction=None):
        '''Nonterminal for one GIVEN definition.'''

        if restriction and self.sym != restriction:
            self.expect(restriction)

        sym = self.sym
        if self.sym == 'and':           # transforming the 'and'
            sym = 'and_given'

        if item is None:
            item = [ sym, self.text, None ]     # 'given'/'and_given', 'identifier', body list
        self.lex()
        if self.sym == 'when':
            when_lst = self.When_serie([])
            self.addToBodyOf(item, when_lst)
            return tuple(item)

        elif self.sym == 'and':
            t = self.Given(restriction='and')
            self.addToBodyOf(item, [ t ])
            return tuple(item)

        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the WHEN.
            self.lex()
            when_lst = self.When_serie([])
            self.addToBodyOf(item, when_lst)
            return tuple(item)

        elif self.sym == 'endofdata':
            # No more WHENs.
            return when_lst
        else:
            self.expect('when', 'and', 'emptyline', 'endofdata')


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

        elif self.sym == 'scenario':
            # No more WHENs -- another scenario to be processed.
            return when_lst

        elif self.sym == 'endofdata':
            # No more WHENs.
            return when_lst
        else:
            self.expect('when', 'emptyline', 'scenario', 'endofdata')


    def When(self, item=None, restriction=None):
        '''Nonterminal for one WHEN definition.'''

        if restriction and self.sym != restriction:
            self.expect('and')

        sym = self.sym
        if self.sym == 'and':           # transforming the 'and'
            sym = 'and_when'

        if item is None:
            item = [ sym, self.text, None ]       # 'when'/'and_when', 'identifier', body list
        self.lex()
        if self.sym == 'then':
            t = self.Then()
            item.append( [ t ])         # as a body of 'when'
            return tuple(item)

        elif self.sym == 'and':
            t = self.When(restriction='and')
            self.addToBodyOf(item, [ t ])        # 'and_when' as body of 'when'
            return tuple(item)

        elif self.sym == 'emptyline':
            # Ignore the empty line and wait for the WHEN.
            self.lex()
            when_lst = self.When_serie([])
            self.addToBodyOf(item, when_lst)
            return tuple(item)

        else:
            self.expect('then', 'and')


    def Then(self, item=None, restriction=None):
        '''Nonterminal for one THEN definition.'''

        if restriction and self.sym != restriction:
            self.expect('and')

        sym = self.sym
        if self.sym == 'and':           # transforming the 'and'
            sym = 'and_then'

        if item is None:
            item = [ sym, self.text, None ]       # 'then'/'and_then', 'identifier', body list
        self.lex()

        if self.sym == 'and':
            t = self.Then(restriction='and')
            self.addToBodyOf(item, [ t ])
            return tuple(item)

        elif self.sym == 'emptyline':
            self.lex()
            return self.Then(item, restriction='and')

        elif self.sym == 'scenario':
            self.addToBodyOf(item, [])  # no more nesting
            return tuple(item)

        else:
            self.expect('then', 'and', 'scenario')



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