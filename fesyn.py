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

        self.lextoken = None    # tuple with elements (extracted to...)
        self.sym   = None       # symbol like 'scenario'
        self.text  = None       # value like 'abc'
        self.lexem = None       # lexem like 'Scenario: abc [tag1][tag2]'
        self.tags  = None       # extra_info like '[tag1][tag2]'

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


    #-------------------------------------------------------------------------
    def Start(self):
        """Implements the start nonterminal.
        """
        self.Feature_or_story()
        self.Test_case_or_scenario_serie()
        self.expect('$')
        return self.syntax_tree


    def Empty_lines(self):
        """Nonterminal for the sequence of zero or more 'emptyline' tokens.
        """
        if self.sym == 'emptyline':
            self.lex()
            self.Empty_lines()


    #-------------------------------------------------------------------------
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
        elif self.sym in ('given', 'when', 'then', 'and', 'but', 'section'):
            # False recognition inside the description. The element must
            # be consumed as line (including the keyword); hence,
            # the lexem but with the newline stripped out.
            descr_lst.append(self.lexem.rstrip())
            self.lex()
            self.Description(descr_lst)


    def Test_case_or_scenario_serie(self):
        """Nonterminal for a serie of test-case or scenario definitions.
        """
        self.Empty_lines()
        if self.sym == 'test_case':
            self.Test_case()
            self.Test_case_or_scenario_serie()
        elif self.sym == 'scenario':
            self.Scenario()
            self.Test_case_or_scenario_serie()


    #-------------------------------------------------------------------------
    def Test_case(self, item=None):
        """Nonterminal for one TEST_CASE.
        """
        bodylst = []
        item = [self.sym, self.text, bodylst]     # 'test_case', 'id', body
        self.syntax_tree.append(tuple(item))

        self.lex()
        self.Empty_lines()
        if self.sym == 'section':
            self.Section_serie(bodylst)


    def Section_serie(self, upperlst):
        """Zero or more SECTION items (at the same level).
        """
        self.Empty_lines()      # necessary for the recursion
        if self.sym == 'section':
            self.Section(upperlst)
            self.Empty_lines()
            self.Section_serie(upperlst)


    def Section(self, upperlst):
        """Nonterminal for one SECTION definition.
        """
        assert self.sym == 'section'
        bodylst = []                     # body of the section item
        item = [self.sym, self.text, bodylst] # 'section', 'id', body
        upperlst.append(tuple(item))     # ready to be appended
        self.lex()


    #-------------------------------------------------------------------------
    def Scenario(self):
        """Nonterminal for one Scenario.
        """
        assert self.sym == 'scenario'
        bodylst = []
        item = [self.sym, self.text, bodylst]
        self.syntax_tree.append(tuple(item))

        self.lex()
        self.Empty_lines()
        if self.sym == 'given':
            self.Given_serie(bodylst) # nested to the body of the scenario


    def Given_serie(self, upperlst):
        """Zero or more GIVEN items (at the same level).
        """
        self.Empty_lines()      # neccessary for the recursion
        if self.sym == 'given':
            self.Given(upperlst)
            self.Given_serie(upperlst)


    def Given(self, upperlst):
        """Nonterminal for one GIVEN definition.
        """
        assert self.sym == 'given'
        bodylst = []                     # body of the given item
        item = [self.sym, self.text, bodylst] # 'given', 'id', body
        upperlst.append(tuple(item))     # ready to be appended

        self.lex()
        self.Empty_lines()
        if self.sym == 'when':
            self.When_serie(bodylst)    # nested to the given
        elif self.sym == 'and':
            self.sym = 'and_given'      # symbol transformation
            self.And_given(bodylst)     # nested to the given
        elif self.sym == 'but':         # but s transformed to and_given
            self.sym = 'and_given'      # symbol transformation
            self.And_given(bodylst)     # nested to the given
        elif self.sym == 'given':
            self.Given(upperlst)        # nested to the scenario body


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
            self.sym = 'and_given'      # symbol transformation
            self.And_given(bodylst)     # nested to the given
        elif self.sym == 'but':         # but s transformed to and_given
            self.sym = 'and_given'      # symbol transformation
            self.And_given(bodylst)     # nested to the given


    def When_serie(self, upperlst):
        """Nonterminal for a serie of WHEN definitions.
        """
        self.Empty_lines()      # neccessary for the recursion
        if self.sym == 'when':
            self.When(upperlst)
            self.When_serie(upperlst)


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
        elif self.sym == 'but':         # but s transformed to and_when
            self.sym = 'and_when'       # symbol transformation
            self.And_when(bodylst)      # nested to the WHEN


    def And_when(self, upperlst):
        """Nonterminal for one AND_WHEN definition.
        """
        assert self.sym == 'and_when'
        bodylst = []                     # of the when item
        item = [self.sym, self.text, bodylst] # 'when'/'and_when', 'id', body
        upperlst.append(tuple(item))     # when appended to the upperlst

        self.lex()
        self.Empty_lines()
        if self.sym == 'then':
            self.Then(bodylst)          # always nested to WHEN
        elif self.sym == 'and':
            self.sym = 'and_when'       # symbol transformation
            self.And_when(bodylst)      # nested to WHEN
        elif self.sym == 'but':         # but s transformed to and_when
            self.sym = 'and_when'       # symbol transformation
            self.And_when(bodylst)      # nested to the WHEN


    def Then(self, upperlst):
        """Nonterminal for one THEN definition.
        """
        assert self.sym == 'then'
        bodylst = []
        item = [self.sym, self.text, bodylst] # 'then'/'and_then', 'id', body
        upperlst.append(tuple(item))     # appended to the upper then-item

        self.lex()
        self.Empty_lines()
        if self.sym == 'and':
            self.sym = 'and_then'       # symbol transformation
            self.And_then(bodylst)      # nested to the previous then-item


    def And_then(self, upperlst):
        """Nonterminal for one AND_THEN definition.
        """
        assert self.sym == 'and_then'
        bodylst = []
        item = [self.sym, self.text, bodylst] # 'then'/'and_then', 'id', body
        upperlst.append(tuple(item))    # appended to the upper then-item

        self.lex()
        self.Empty_lines()
        if self.sym == 'and':
            self.sym = 'and_then'       # symbol transformation
            self.And_then(bodylst)      # nested to the previous then-item


#-----------------------------------------------------------------------

if __name__ == '__main__':
    # This is only a trivial example. Have a look at
    # the pyunittests/fesynTest.py that contains the tests.
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