#!python3

import re

# The Catch-defined identifiers are considered keywords for this purpose.
# Also the BDD text that were generated into comments are considered
# keywords for the purpose, because we want to reconstruct the *.feature
# file information from the comment. The matched keyword may have more
# forms (think about the human language used for keywords in comments).
#
# The following list of rules contain the tuples with the following
# meaning...
#
# The first element determines the method of recognition of the item:
# 0 - exact char sequence, 1 - regular character pattern.
#
# The second element capture the sequence of the regular expression pattern.
#
# The third element is the lex item identifier.
#
rules = [
#    (1, re.compile(r'Feature|Požadavek', re.I),  'feature'),

    (0, 'SCENARIO',     'scenario'),
    (0, 'GIVEN',        'given'),
    (0, 'WHEN',         'when'),
    (0, 'THEN',         'then'),
    (0, 'TEST_CASE',    'test_case'),
    (0, 'SECTION',      'section'),

    (0, '(',            'lpar'),
    (0, ')',            'rpar'),
    (0, '{',            'lbrace'),
    (0, '}',            'rbrace'),
    (0, '\n',           'newline'),

#    (1, re.compile(r'.*\n'),        'line')         # default for the rest
]


def build_str_closures(s, lexid, container, iterator):

    def match_str(container, iterator):
        print('called match_str:', (s, iterator.pos))
        return container.source.startswith(s, iterator.pos)

    def result_str(container, iterator):
        print('called result_str:', (lexid, s, iterator.pos))
        return lexid, s, iterator.pos + len(s)
        
    return (match_str, result_str)    


def match_rex(pattern, container, iterator):
    print('called match_rex:', (pattern, iterator.pos))
    return container.source.startswith(s, iterator.pos)


def buildMatchAndResultFunctions(container, iterator):
    '''Builds the list of (match_fn, result_fn) closures for the rules.'''
    
    print('buildMatchAndResultFunctions started')
    # As a container can be iterated by several iterators, both the container
    # and the iterator must be passed (not captured inside the closures).
    # The rules are defined by the global one; hence, captured inside
    functions = []

    for method, pattern, lexid in rules:
        print((method, pattern, lexid))
        if method == 0:
            functions.append(build_str_closures(pattern, lexid, container, iterator))
            print('append')

    print('buildMatchAndResultFunctions is to be finished')
    return functions



class LexIterator:

    def __init__(self, container, startpos):
        print('iterator initialized')
        self.container = container
        self.pos = startpos

        self.match_and_result_fns = buildMatchAndResultFunctions(container, self)


    def __iter__(self):
        return self


    def __next__(self):
        # Loop through the closure pairs to find the lex item.
        print('__next__ started')

        # When the match is found, return early.
        for match_fn, result_fn in self.match_and_result_fns:
            print('before match_fn:', self.pos)
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
        print('iterator to be created')
        return LexIterator(self, 0)


    def __repr__(self):
        return repr((self.sourcenameinfo, self.lineno, self.line))


    def __str__(self):
        return self.line



if __name__ == '__main__':

    import textwrap
    container = LexContainer(textwrap.dedent('''\
                        SCENARIO("vectors can be sized and resized") {
                        GIVEN("A vector with some items") {
                            WHEN("more capacity is reserved") {
                                THEN("the capacity changes but not the size") {
                                }
                            }
                        }'''))
    for lexid, value in container:
        print( (lexid, value) )