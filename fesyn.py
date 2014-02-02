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
        self.scenario_body = None
        self.given_body = None


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


#    def add_to_body_of(self, item, arg):
#        """Adds the arg to the body list of the item tuple.
#
#        The body list is the third argument of the item.
#        The arg can be or list or element.
#        """
#        assert item[2] is not None
#        if isinstance(arg, list):
#            item[2].extend(arg)
#        else:
#            item[2].append(arg)


    def Start(self):
        """Implements the start nonterminal.
        """
        self.Feature_or_story()
        self.Test_case_or_scenario()
        self.expect('$')
        return self.syntax_tree


    def Empty_lines(self):
        """Nonterminal for the sequence of zero or more 'emptyline' tokens.
        """
        if self.sym == 'emptyline':
            self.lex()
            self.Empty_lines()


    def Feature_or_story(self):
        """Nonterminal for processing the story/feature definition.
        """
        self.Empty_lines()
        if self.sym in ('story', 'feature'):
            self.syntax_tree.append((self.sym, self.text))
            self.lex()
            self.Empty_lines()
            descr_lst = []
            self.Description(descr_lst)
            if descr_lst:
                self.syntax_tree.append( ('description', descr_lst) )
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
            self.Description(descr_lst)


    def Test_cases_or_scenarios(self):
        """Nonterminal for a serie of test-case or scenario definitions.
        """
        self.Empty_lines()
        if self.sym == 'test_case':
            self.Test_case()
            self.Test_cases_or_scenarios()
        elif self.sym == 'scenario':
            self.Scenario()
            self.Test_cases_or_scenarios()
        elif self.sym == '$':
            pass        # no test_case or scenario is acceptable
        else:
            self.expect('test_case', 'scenario', '$')


    def Test_case(self, item=None):
        """Nonterminal for one TEST_CASE.
        """
        bodylst = []
        item = [self.sym, self.text, bodylst]     # 'test_case', 'id', body
        self.syntax_tree.append(tuple(item))

        self.lex()
        self.Empty_lines()
        if self.sym == 'section':
            self.Section(bodylst)
        elif self.sym == '$':
            pass        # no section -- logically missing but acceptable
        else:
            self.expect('section', '$')


    def Scenario(self):
        """Nonterminal for one Scenario.
        """
        assert self.sym == 'scenario'
        assert self.scenario_body is None

        self.scenario_body = []
        item = [self.sym, self.text, self.scenario_body]
        self.syntax_tree.append(tuple(item))

        self.lex()
        self.Empty_lines()
        if self.sym == 'given':
            self.Given(self.scenario_body) # nested to the body of the scenario
        elif self.sym == 'scenario':
            # The previous scenario had no definition. It exists and have
            # the identifier (i.e. someone was thinking about it during
            # analysis, but the scenario was not specified yet).
            self.scenario_body = None
            self.Scenario()
        elif self.sym == '$':
            pass        # no given, but acceptable
        else:
            self.expect('given', 'scenario', '$')


#    def Given_serie(self, given_lst):
#        """Nonterminal for a serie of GIVEN definitions.
#        """
#        if self.sym == 'given':
#            t = self.Given()
#            given_lst.append(t)
#            self.Empty_lines()
#            return self.Given_serie(given_lst)
#        elif self.sym == 'scenario':
#            # No more GIVENs -- another scenario to be processed.
#            return given_lst
#        elif self.sym == '$':
#            # No more GIVENs.
#            return given_lst
#        else:
#            self.expect('given', 'emptyline', 'scenario', '$')


    def Given(self):
        """Nonterminal for one GIVEN definition.

        The restriction can be 'and' that is converted to and_given
        and nested recursively -- unlike the explicit 'given' serie
        that adds to the upperlist.
        """
        assert self.sym == 'given'
        self.given_body = []             # body of the given item
        item = [sym, self.text, self.given_body] # 'given', 'id', body
        upperlst.append(tuple(item))     # ready to be appended

        self.lex()
        self.Empty_lines()
        if self.sym == 'when':
            self.given_body
            self.When(self.given_body)  # nested to the given
        elif self.sym == 'and':
            self.And_given(self.given_body) # nested to the given
        elif self.sym == 'given':
            self.Given()                # nested to the scenario body
        elif self.sym == '$':
            pass # no WHENs -- missing logically, but acceptable
        else:
            self.expect('when', 'and', 'given', '$')


    def And_given(self, upperlst):
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
            self.And_given(bodylst)     # nested to the given
        elif self.sym == 'given':
            self.Given(self.scenario_body) # nested to the scenario body
        elif self.sym == '$':
            pass # no WHENs -- missing logically, but acceptable
        else:
            self.expect('when', 'and', 'given', '$')


#    def When_serie(self, when_lst, restriction=None):
#        """Nonterminal for a serie of WHEN definitions.
#        """
#        if self.sym == 'when':
#            t = self.When(restriction=restriction)
#            when_lst.append(t)
#            self.Empty_lines()
#            return self.When_serie(when_lst)
#        elif self.sym == 'scenario':
#            # No more WHENs -- another scenario to be processed.
#            return when_lst
#        elif self.sym == '$':
#            # No more WHENs.
#            return when_lst
#        else:
#            self.expect('when', 'emptyline', 'scenario', '$')


    def When(self, upperlst):
        """Nonterminal for one WHEN definition.
        """
        assert self.sym == 'when'

        bodylst = []                    # of the when item
        item = [self.sym, self.text, bodylst] # 'when', 'id', body
        upperlst.append(tuple(item))    # when appended to the upperlst

        self.lex()
        self.Empty_lines()
        if self.sym == 'then':
            self.Then(bodylst)          # always nested to WHEN
        elif self.sym == 'and':
            self.sym = 'and_when'       # symbol transformation
            self.And_when(bodylst)      # nested to WHEN
        elif self.sym == 'when':
            self.When(upperlst)         # appended to the upperlst
        elif self.sym == '$':
            pass        # no THEN -- missing logically, but acceptable
        else:
            self.expect('then', 'and', 'when', '$')


    def And_when(self, upperlst):
        """Nonterminal for one AND_WHEN definition.
        """
        assert self.sym == 'and_when'

        bodylst = []                     # of the when item
        item = [sym, self.text, bodylst] # 'when'/'and_when', 'id', body
        upperlst.append(tuple(item))     # when appended to the upperlst

        self.lex()
        self.Empty_lines()
        if self.sym == 'then':
            self.Then(bodylst)          # always nested to WHEN
        elif self.sym == 'and':
            self.When(bodylst, 'and')   # nested to WHEN
        elif self.sym == 'when':
            self.When(upperlst)         # appended to the upperlst
        elif self.sym == '$':
            pass        # no THEN -- missing logically, but acceptable
        else:
            self.expect('then', 'and', 'when', '$')


    def Then(self, upperlst, restriction=None):
        """Nonterminal for one THEN definition.

        The restriction can be 'and' that is converted to and_then
        and nested recursively. The the explicit 'then' serie at the
        same level probably does not make sense.
        """
        if restriction and self.sym != restriction:
            self.expect('and')
        sym = self.sym
        if self.sym == 'and':           # transforming the 'and'
            sym = 'and_then'
        assert sym in ('then', 'and_then')

        bodylst = []
        item = [sym, self.text, bodylst] # 'then'/'and_then', 'id', body
        upperlst.append(tuple(item))     # appended to the upper then-item

        self.lex()
        self.Empty_lines()
        if self.sym == 'and':
            self.Then(bodylst, 'and')   # nested to the previous then-item
        elif self.sym in ('when', 'scenario', '$'):
            pass
        else:
            self.expect('and', 'when', 'scenario', '$')



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