#!python3
# -*- coding: utf-8 -*-
'''Lexical analysis for the Catch test sources.'''

import re

# The Catch-defined identifiers are considered keywords for this purpose.
# Also the BDD text that were generated into comments are considered
# keywords for the purpose -- that is because we want to reconstruct
# the *.feature file information from the comment. The matched keyword
# may have more forms (think about more human languages used for keywords
# in comments).
#
# The following list of rules contain the tuples with the following
# meaning...
#
# The first element determines the method of recognition of the item:
# 0 - exact char sequence, 1 - regular character pattern.
#
# The second element captures depends on the on the first element.
# Or it is the exact string, or it is a regular expression pattern.
#
# The third element is the lex item identifier.
#
# The following rules are evaluated in this order. The order can
# be important sometimes (see testing whitespaces only after newline).
#
rules = [
    (1, r'"[^"]*"',     'dqstrlit'),    # double quoted string literal

    (0, 'SCENARIO',     'scenario'),
    (0, 'GIVEN',        'given'),
    (0, 'WHEN',         'when'),
    (0, 'THEN',         'then'),
    (0, 'TEST_CASE',    'test_case'),
    (0, 'SECTION',      'section'),

    (0, ':',            'colon'),
    (0, '(',            'lpar'),
    (0, ')',            'rpar'),
    (0, '{',            'lbrace'),
    (0, '}',            'rbrace'),
    (0, '"',            'dquote'),
    (0, '\n',           'newline'),
    (0, '//',           'endlcomment'),

    (1, r'\s+',         'whitespaces'),      # must be tested after \n

    (1, r'(?i)(User\s+)?Story',            'story'),
    (1, r'(?i)(Uživatelský\s+)?Požadavek', 'story'),
    (1, r'(?i)Feature',         'feature'),
    (1, r'(?i)Rys',             'feature'),

    (1, r'[^\n]+',              'restofline')   # default for the rest
]


def build_str_closures(s, lexid, container, iterator):
    '''Builds the pair of closures for recognizing exact strings.'''

    def match_str(container, iterator):
        return container.source.startswith(s, iterator.pos)

    def result_str(container, iterator):
        return lexid, s, iterator.pos + len(s)

    return (match_str, result_str)


def build_rex_closures(pattern, lexid, container, iterator):
    '''Builds the pair of closures for the regex pattern.'''

    def match_rex(container, iterator):
        # Actually returns a match object that can be interpreted
        # in a boolean context as True/False (matches/does not match).
        rex = re.compile(pattern)
        return rex.match(container.source[iterator.pos:])

    def result_rex(container, iterator):
        m = match_rex(container, iterator)  # see the match_rex() above
        s = m.group(0)                      # the matched text
        return lexid, s, iterator.pos + len(s)

    return (match_rex, result_rex)


def buildMatchAndResultFunctions(container, iterator):
    '''Builds the list of (match_fn, result_fn) closures for the rules.'''

    # As a container can be iterated by several iterators, both the container
    # and the iterator must be passed (not captured inside the closures).
    # The rules are defined by the global one; hence, captured inside
    functions = []

    for method, x, lexid in rules:      # x is or string or regex
        if method == 0:
            # Here x is a string.
            functions.append(build_str_closures(x, lexid, container, iterator))
        elif method == 1:
            # Here x is a compiled regular expression.
            functions.append(build_rex_closures(x, lexid, container, iterator))
        else:
            raise NotImplementedError

    return functions



class LexIterator:

    def __init__(self, container, startpos):
        self.container = container
        self.pos = startpos

        self.match_and_result_fns = buildMatchAndResultFunctions(container, self)


    def __iter__(self):
        return self


    def __next__(self):
        # Loop through the closure pairs to find the lex item.
        # When the match is found, return early.
        for match_fn, result_fn in self.match_and_result_fns:
            if match_fn(self.container, self):
                lexid, text, newpos = result_fn(self.container, self)
                self.pos = newpos
                return lexid, text

        # The match was not found. Or it is a default, or there is nothing
        # to iterate through.
        if self.pos < len(self.container.source):
            text = self.container.source[self.pos:]
            self.pos = len(self.container.source)
            return 'rest', text
        else:
            raise StopIteration


class LexContainer:
    '''Lexical parsing the Catch-test source multiline string.

    Implemented as the iterable container.
    '''

    def __init__(self, source):
        self.source = source    # the multiline string


    def __iter__(self):
        return LexIterator(self, 0)


    def __repr__(self):
        return repr((self.sourcenameinfo, self.lineno, self.line))


    def __str__(self):
        return self.line



if __name__ == '__main__':

    import textwrap
    container = LexContainer(textwrap.dedent('''\
                        // Story: this is a user story approach
                        // Uživatelský požadavek: this is the same in Czech
                        //
                        SCENARIO("vectors can be sized and resized") {
                        GIVEN("A vector with some items") {
                            WHEN("more capacity is reserved") {
                                THEN("the capacity changes but not the size") {
                                }
                            }
                        }'''))
    for lexid, value in container:
        print( (lexid, value) )