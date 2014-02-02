#!python3
"""Syntactic analysis for the *.feature files.

Notice that some of the method of the SyntacticAnalyzerForFeature class
start with capital letters. This is not ignorance of the usual style.
The methods implement recursive parsing of the related nonterminals.
"""

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
        """Get the next lexical token.
        """
        try:
            self.lextoken = next(self.it)
            ##print(self.lextoken)
            self.sym, self.text, self.lexem, self.tags = self.lextoken
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
                        source_name, line_no, self.sym, self.text)
            raise RuntimeError(msg)


    def add_to_body_of(self, item, lst):
        """Adds list of items lst to the item body list.
        """
        if item[2] is None:
            item[2] = lst
        else:
            item[2].extend(lst)


    def Start(self):
        """Implements the start nonterminal.
        """
        self.Feature_or_story()
        self.Test_case_serie()
        self.expect('$')
        return self.syntax_tree


    def Empty_lines(self):
        """Nonterminal for the sequence of zero or more 'emptyline' tokens.
        """
        while self.sym == 'emptyline':
            self.lex()


    def Feature_or_story(self):
        """Nonterminal for processing the story/feature definition.
        """
        self.Empty_lines()
        if self.sym in ('story', 'feature'):
            self.syntax_tree.append( (self.sym, self.text) )
            self.lex()
            self.Empty_lines()
            descr_lst = self.Description([])
            if descr_lst:
                self.syntax_tree.append( ('description', '\n'.join(descr_lst)) )
        elif self.sym in ('$', 'scenario', 'test_case'):
            pass # empty source, or no story definition, nor feature def
        else:
            self.expect('story', 'feature', '$', 'scenario', 'test_case')


    def Description(self, descr_lst):
        """Nonterminal for description lines of the story/feature.
        """
        if self.sym in ('emptyline', 'line'):
            # The emptylines were skipped before calling this method for
            # the first time. However, next emptylines may be a part
            # of this description.
            descr_lst.append(self.text)
            self.lex()
            return self.Description(descr_lst)
        else:
            return descr_lst


    def Test_case_serie(self):
        """Nonterminal for a serie of test-case or scenario definitions.
        """
        self.Empty_lines()
        if self.sym == 'test_case':
            t = self.Test_case()
            self.syntax_tree.append(t)
            self.Test_case_serie()
        elif self.sym == 'scenario':
            t = self.Scenario()
            self.syntax_tree.append(t)
            self.Test_case_serie()
        elif self.sym == '$':
            pass        # that's OK, no test_source or scenario is acceptable
        else:
            self.expect('test_case', 'scenario', '$', 'emptyline')


    def Test_case(self, item=None):
        """Nonterminal for one TEST_CASE.
        """
        if item is None:
            item = [self.sym, self.text, None]
        self.lex()
        self.Empty_lines()
        if self.sym == 'section':
            sec_lst = self.Section_serie([])
            self.add_to_body_of(item, sec_lst)
            return tuple(item)
        elif self.sym == '$':
            # Empty body of the test_case (that is no section).
            self.add_to_body_of(item, [])
            return tuple(item)
        else:
            self.expect('section', 'emptyline', '$')


    def Scenario(self):
        """Nonterminal for one Scenario.
        """
        item = [self.sym, self.text, None]      # specific symbol: 'scenario'
        self.lex()
        self.Empty_lines()
        if self.sym == 'given':
            given_lst = self.Given_serie([])
            self.add_to_body_of(item, given_lst)
            return tuple(item)
        elif self.sym == '$':
            # Empty body of the scenario (that is no given...).
            self.add_to_body_of(item, [])
            return tuple(item)
        else:
            self.expect('given', 'emptyline', '$')


    def Given_serie(self, given_lst):
        """Nonterminal for a serie of GIVEN definitions.
        """
        if self.sym == 'given':
            t = self.Given()
            given_lst.append(t)
            self.Empty_lines()
            return self.Given_serie(given_lst)
        elif self.sym == 'scenario':
            # No more GIVENs -- another scenario to be processed.
            return given_lst
        elif self.sym == '$':
            # No more GIVENs.
            return given_lst
        else:
            self.expect('given', 'emptyline', 'scenario', '$')


    def Given(self, item=None, restriction=None):
        """Nonterminal for one GIVEN definition.
        """
        if restriction and self.sym != restriction:
            self.expect(restriction)
        sym = self.sym
        if self.sym == 'and':           # transforming the 'and'
            sym = 'and_given'
        if item is None:
            item = [sym, self.text, None]     # 'given'/'and_given', 'identifier', body list
        self.lex()
        self.Empty_lines()
        if self.sym == 'when':
            when_lst = self.When_serie([])
            self.add_to_body_of(item, when_lst)
            return tuple(item)
        elif self.sym == 'and':
            t = self.Given(restriction='and')
            self.add_to_body_of(item, [t])
            return tuple(item)
        elif self.sym == '$':
            # No more WHENs.
            self.add_to_body_of(item, [])
            return tuple(item)
        else:
            self.expect('when', 'and', 'emptyline', '$')


    def When_serie(self, when_lst, restriction=None):
        """Nonterminal for a serie of WHEN definitions.
        """
        if self.sym == 'when':
            t = self.When(restriction=restriction)
            when_lst.append(t)
            self.Empty_lines()
            return self.When_serie(when_lst)
        elif self.sym == 'scenario':
            # No more WHENs -- another scenario to be processed.
            return when_lst
        elif self.sym == '$':
            # No more WHENs.
            return when_lst
        else:
            self.expect('when', 'emptyline', 'scenario', '$')


    def When(self, item=None, restriction=None):
        """Nonterminal for one WHEN definition.
        """
        if restriction and self.sym != restriction:
            self.expect('and')
        sym = self.sym
        if self.sym == 'and':           # transforming the 'and'
            sym = 'and_when'
        if item is None:
            item = [sym, self.text, None]       # 'when'/'and_when', 'identifier', body list
        self.lex()
        self.Empty_lines()
        if self.sym == 'then':
            t = self.Then()
            self.add_to_body_of(item, [t])        # as a body of 'when'
            return tuple(item)
        elif self.sym == 'and':
            t = self.When(restriction='and')
            self.add_to_body_of(item, [t])        # 'and_when' as body of 'when'
            return tuple(item)
        else:
            self.expect('then', 'and')


    def Then(self, item=None, restriction=None):
        """Nonterminal for one THEN definition.
        """
        if restriction and self.sym != restriction:
            self.expect('and')
        sym = self.sym
        if self.sym == 'and':           # transforming the 'and'
            sym = 'and_then'

        if item is None:
            item = [sym, self.text, None]       # 'then'/'and_then', 'identifier', body list
        self.lex()
        self.Empty_lines()
        if self.sym == 'and':
            t = self.Then(restriction='and')
            self.add_to_body_of(item, [ t ])
            return tuple(item)
        elif self.sym == 'scenario':
            self.add_to_body_of(item, [])  # no more nesting
            return tuple(item)
        elif self.sym == '$':
            self.add_to_body_of(item, [])  # no more nesting
            return tuple(item)
        else:
            self.expect('then', 'and', 'scenario')



#-----------------------------------------------------------------------

if __name__ == '__main__':
    source = textwrap.dedent("""\
        Story: story identifier

          As a user
          I want the feature
          so that my life is to be easier.

        Scenario: scenario identifier
           Given: given identifier
            When: when identifier
            Then: then identifier
        """)
    print('source:', source)
    sa = SyntacticAnalyzerForFeature(source)
    tree = sa.Start()   # run from the start nonterminal
    print(tree)