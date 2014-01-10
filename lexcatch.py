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
# be important sometimes.
#
rules = [
    (0, '\\',           'esc'),         # escaping char
    (0, ':',            'colon'),
    (0, '(',            'lpar'),
    (0, ')',            'rpar'),
    (0, '{',            'lbrace'),
    (0, '}',            'rbrace'),

##    (1, r'"[^"]*"',     'dqstrlit'),    # double quoted string literal
    (0, '"',            'dquote'),

    (0, '\n',           'newline'),

    (0, '//',           'commentendl'),   # C++ comment till the end of line
    (0, '/*',           'commentlpar'),   # C-comment started
    (0, '*/',           'commentrpar'),   # C-comment finished

    (0, 'SCENARIO',     'scenario'),
    (0, 'GIVEN',        'given'),
    (0, 'WHEN',         'when'),
    (0, 'THEN',         'then'),
    (0, 'TEST_CASE',    'test_case'),
    (0, 'SECTION',      'section'),

    (1, r'[ \t]',       'whitespaces'),   # ... except the '\n'

    (1, r'(?i)(User\s+)?Story',            'story'),
    (1, r'(?i)(Uživatelský\s+)?Požadavek', 'story'),
    (1, r'(?i)Feature',         'feature'),
    (1, r'(?i)Rys',             'feature'),

    (1, r'[^"\\\n\t ]+', 'str'), # a string until esc, whitespace or dquote
    (1, r'[^\n]+',       'unrecognized')   # ... until the end of the line
]

#-----------------------------------------------------------------------

def build_lex_str_closures(s, lexid, container, iterator):
    '''Builds the pair of closures for recognizing exact strings.'''

    def match_str(container, iterator):
        return container.source.startswith(s, iterator.pos)

    def result_str(container, iterator):
        return lexid, s, iterator.pos + len(s)

    return (match_str, result_str)

#-----------------------------------------------------------------------

def build_lex_rex_closures(pattern, lexid, container, iterator):
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

#-----------------------------------------------------------------------

def buildMatchAndResultFunctions(container, iterator):
    '''Builds the list of (match_fn, result_fn) closures for the rules.'''

    # As a container can be iterated by several iterators, both the container
    # and the iterator must be passed (not captured inside the closures).
    # The rules are defined by the global one; hence, captured inside
    functions = []

    for method, x, lexid in rules:      # x is or string or regex
        if method == 0:
            # Here x is a string.
            functions.append(build_lex_str_closures(x, lexid, container, iterator))
        elif method == 1:
            # Here x is a compiled regular expression.
            functions.append(build_lex_rex_closures(x, lexid, container, iterator))
        else:
            raise NotImplementedError

    return functions

#-----------------------------------------------------------------------

class Iterator:
    '''Iterates over the Container and returns lexical elements.'''

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

#-----------------------------------------------------------------------

class Container:
    '''Iterable container for lexical parsing of the Catch-test source.

    The source is passed as a multiline string.
    '''

    def __init__(self, source):
        self.source = source    # the multiline string


    def __iter__(self):
        return Iterator(self, 0)


    def __repr__(self):
        return repr((self.sourcenameinfo, self.lineno, self.line))


    def __str__(self):
        return self.line

#-----------------------------------------------------------------------

def parse(source):
    container = Container(source)       # get ready for lexical parsing
    lexlst = list(container)            # get the list of lexical items
    for item in synParse(lexlst):       # result of syntactic parsing
        yield item


def synParse(lexlst):
    synlst = []         # the result with syntactic elements
    lexsublst = []      # lexical elements for unknown syntax

    pos = 0
    while pos < len(lexlst):
        lexid, value = lexlst[pos]
        print(pos, lexid, end=' ')
        if lexid in ('commentendl', 'commentlpar'):     # comment
            item, pos = commentParse(lexlst, pos, lexid)
            synlst.extend(item)
            lexsublst = []      # sublist already present in the syntactic item
#         elif lexid == 'scenario':                       # scenario
#             item, pos = scenarioParse(lexlst, pos, lexid)
#             synlst.extend(item)
#             lexsublst = []
#         elif lexid == 'empty':                          # empty line
#             item, pos = emptyParse(lexlst, pos, lexid)
#             lexsublst = []
#             synlst.extend(item)
        else:
            lexsublst.append(lexlst[pos])               # another lexem
            pos += 1

    if lexsublst:
        synlst.append( ('synParse', 'unknown', lexsublst) )

    return synlst


def commentParse(lexlst, pos, lexid):
    synlst = []         # the result with syntactic elements
    lexsublst = []         # for unrecognized lexems

    if lexid == 'commentendl':                          # C++ comment //
        item, pos = commentEndlParse(lexlst, pos, lexid)
        synlst.extend(item)
        lexsublst = []      # sublist already present in the syntactic item
    elif lexid == 'commentlpar':                        # C comment /*
        item, pos = commentCParse(lexlst, pos, lexid)
        synlst.extend(item)
        lexsublst = []
    else:
        lexsublst.append(lexlst[pos])   # another lexem
        pos += 1

    if lexsublst:
        synlst.append( ('commentParse', 'unknown', lexsublst) )

    return synlst, pos


def commentEndlParse(lexlst, pos, lexid):
    assert lexid == 'commentendl'
    synlst = []
    lexsublst = [ lexlst[pos] ]         # first lexem of the C++ comment
    pos += 1
    lexid, value = lexlst[pos]
    while pos < len(lexlst):
        if lexid == 'story':
            lst, pos = storyParse(lexlst, pos, lexid)
            synlst.extend(lst)
            lexsublst = []
        elif lexid == 'feature':
            lst, pos = featureParse(lexlst, pos, lexid)
            synlst.extend(lst)
            lexsublst = []
        elif lexid == 'newline':
            lexsublst.append(lexlst[pos])       # newline quits the loop
            pos += 1
            break
        else:
            lexsublst.append(lexlst[pos])       # another lexem
            pos += 1

    if lexsublst:
        synlst.append( ('commentEndlParse', 'unknown', lexsublst))

    return synlst, pos


def scenarioParse(lexlst, pos, lexid):
    assert lexid == 'scenario'
    lexsublst = [ lexlst[pos] ]         # first lexem of the scenario
    return ('scenarioParse', 'not implemented', lexsublst), pos + 1


def emptyParse(lexlst, pos, lexid):
    assert lexid == 'empty'
    lexsublst = [ lexlst[pos] ]         # first lexem of the scenario
    return ('emptyParse', 'not implemented', lexsublst), pos + 1


#-----------------------------------------------------------------------

if __name__ == '__main__':
    # This is not a serious unit test -- just for initial debugging.
    # Let the following Catch source was written manually and is maintained
    # by a programmer.
    import textwrap
    source = textwrap.dedent('''\
        // Story: BDD oriented description/testing of the problem
        //
        //    As a normal user
        //    I want to capture "my view" to the subproblem as normal sentences
        //    so that it does not enforce the knowledge of programming.
        //
        SCENARIO( "name for \\"my\\" scenario", "[taga][tagb]" ) {
            GIVEN( "some initial state" ) {
                // set up initial state

                WHEN( "an operation is performed" ) {
                    // perform operation

                    THEN( "we arrive at some expected state" ) {
                        // assert expected state
                    }
                }
            }
        }''')

    source = textwrap.dedent('''\
        SCENARIO( "name for my scenario" ) {
            GIVEN( "some initial state" ) {
                WHEN( "an operation is performed" ) {
                    THEN( "we arrive at some expected state" ) {
                    }
                }
            }
        }''')

    source = textwrap.dedent('''\
        SCENARIO( "name for my scenario" ) {
        }''')

    source = textwrap.dedent('''\
        SCENARIO( "name for my scenario" ) {
        }''')

    # Lexical parsing.
    print('-' * 50, '  lexical parsing')
    container = Container(source)
    lexlst = list(container)
    for lexid, value in lexlst:
        print( (lexid, value) )

    # Now a trivial reconstruction of the lex items back to the source content.
    print('-' * 50, '  lexems back to the source')
    source = ''.join(value for lexid, value in lexlst)
    print(source)

    # Extracting higher-level elements (syntactic parsing).
    print('-' * 50, '  syntactic parsing')
    for synitem in parse(source):
        print(synitem)