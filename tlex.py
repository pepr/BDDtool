#!python3
# -*- coding: utf-8 -*-
'''Lexical analysis for the Catch test sources.'''

import re

# The Catch-defined identifiers are considered keywords for this purpose.
# The following list of items contain the tuples with the following
# meaning. The first element captures a pattern. The second element
# is the lexical symbol identifier.
rules = [
    ('(',            'lpar'),
    (')',            'rpar'),
    ('{',            'lbrace'),
    ('}',            'rbrace'),
    (',',            'comma'),

    # Catch identifiers.
    ('SCENARIO',     'scenario'),
    ('GIVEN',        'given'),
    ('WHEN',         'when'),
    ('THEN',         'then'),
    ('AND_WHEN',     'and_when'),
    ('AND_THEN',     'and_then'),
    ('TEST_CASE',    'test_case'),
    ('SECTION',      'section'),
]

#-----------------------------------------------------------------------

def build_lex_closures(s, lexid, container, iterator):
    '''Builds the pair of closures for recognizing exact strings.'''

    def match_str(container, iterator):
        return container.source.startswith(s, iterator.pos)

    def result_str(container, iterator):
        return lexid, s, iterator.pos + len(s)

    return (match_str, result_str)

#-----------------------------------------------------------------------

def buildMatchAndResultFunctions(container, iterator):
    '''Builds the list of (match_fn, result_fn) closures for the rules.'''

    # As a container can be iterated by several iterators, both the container
    # and the iterator must be passed (not captured inside the closures).
    # The rules are defined by the global one; hence, captured inside
    functions = []

    for s, symbol in rules:
        functions.append(build_lex_closures(s, symbol, container, iterator))

    return functions

#-----------------------------------------------------------------------

class Iterator:
    '''Iterates over the Container and returns lexical elements.'''

    def __init__(self, container, startpos):
        self.container = container
        self.pos = startpos

        self.source = self.container.source
        self.srclen = len(self.container.source)

        self.status = 0         # of the finite automaton
        self.symbol = None
        self.lst = []
        self.prelst = []
        self.post = None        # for src reconstruction -- like '*/'

        self.match_and_result_fns = buildMatchAndResultFunctions(container, self)


    def __iter__(self):
        return self


    def notImplemented(self, msg=''):
        raise NotImplementedError('status={}: {!r}'.format(self.status, msg))


    def lexitem(self):
        '''Forms lexical item from the member variables.'''

        # Form the lexical item.
        item = (self.symbol, ''.join(self.lst),
                ''.join(self.prelst), self.post)

        # Warn if symbol was not recognized.
        if self.symbol is None:
            print('Warning: symbol not set for', item)

        # Reset the variables.
        self.symbol = None
        self.lst = []
        self.prelst = []
        self.post = None

        # Return the result.
        return item


    def expected(self, s):
        '''Forms error lexical item.'''

        # Form the lexical item.
        current = (self.symbol, ''.join(self.lst),
                   ''.join(self.prelst), self.post)
        item = ('error', '{!r} expected'.format(s),
                repr(current), None)

        # Reset the variables.
        self.symbol = None
        self.lst = []
        self.prelst = []
        self.post = None

        # Return the result.
        return item


    def __next__(self):
        '''Returns lexical items (symbol, lexem, pre, post).'''

        # Loop until the end of data.
        while self.status != 1000:

            # Get the next character or set the status for the end of data
            if self.pos < self.srclen:
                c = self.source[self.pos]
                self.lst.append(c)
                self.pos += 1           # advanced to the next one
            else:
                # End of data, but the previous element may not be
                # entirely collected/finalized.
                if self.status == 3:    # waiting for end of comment */
                    # The state is not final, return the error
                    error = self.expected('*/')
                    self.status = 800
                    return error
                elif self.status == 2:  # empty // comment just before end of data
                    item = self.lexitem()
                    self.status = 800
                    return item
                elif self.status == 5:  # closing dquote of "literal" missing
                    error = self.expected('"')
                    self.status = 800
                    return error
                else:
                    self.status = 800

            #============================   initial state, nothing known
            if self.status == 0:
                assert self.symbol is None
                if c == '/':            # comment?
                    self.status = 1
                elif c in ' \t':
                    pass                # skip tabs and spaces
                elif c == '\n':
                    self.symbol = 'emptyline'
                    return self.lexitem()
                elif c == '"':          # string literal started
                    self.symbol = 'stringlit'
                    self.prelst = self.lst
                    self.lst = []
                    self.status = 5
                else:
                    # Loop through the closure pairs to find the lex item.
                    # When the match is found, return early.
                    self.pos -= 1       # back from the advanced position
                    del self.lst[-1]    # remove the last char from the list

                    for match_fn, result_fn in self.match_and_result_fns:
                        if match_fn(self.container, self):
                            symbol, lexem, newpos = result_fn(self.container, self)
                            self.pos = newpos
                            self.symbol = symbol
                            self.prelst = self.lst
                            self.lst = [ lexem ]
                            return self.lexitem()

                    # No element found. Something is new, not implemented.
                    self.notImplemented(c)

            #----------------------------   possible start of a comment
            elif self.status == 1:
                if c == '/':
                    # The C++ // comment recognized.
                    self.symbol = 'comment'
                    self.prelst = self.lst
                    self.lst = []
                    self.status = 2     # collect content of // comment
                elif c == '*':
                    # The C /* comment started.
                    self.symbol = 'comment'
                    self.prelst = self.lst
                    self.lst = []
                    self.status = 3     # collect content of the  /* comment */
                else:
                    self.notImplemented(c)

            #----------------------------   comment till the end of line
            elif self.status == 2:
                if c == '\n':
                    # End of line -- form the lex item.
                    self.status = 0
                    return self.lexitem()

                # All other characters are consumed as the comment content.

            #----------------------------   collecting comment till */
            elif self.status == 3:
                if c == '*':
                    self.status = 4     # possibly end of C comment

                # All other characters are consumed as the comment content.

            #----------------------------   comment */ closed
            elif self.status == 4:
                if c == '/':
                    # Here the self.post will be filled with the '*/'.
                    # This is important for the text reconstruction.
                    self.status = 0
                    assert self.post == None
                    self.lst[-2:] = []  # delete, not part of the content
                    self.post = '*/'
                    return self.lexitem()
                elif c == '*':
                    pass                # extra star, stay in this state
                else:
                    self.status = 3     # collecting other chars

            #----------------------------   collecting string literal chars
            elif self.status == 5:
                if c == '"':
                    # String literal finished.
                    self.status = 0
                    self.lst[-1:] = []  # delete, not part of the content
                    self.post = '"'
                    return self.lexitem()
                elif c == '\\':         # backlash starts an escape sequence
                    self.status = 6

                # Any other char collected as a part of the literal.

            #----------------------------   the char after the escape
            elif self.status == 6:
                # Any char after esc was collected to self.lst. Now
                # back to collecting other characters of the string literal
                self.status = 5

            #----------------------------   end of data
            elif self.status == 800:
                self.symbol = 'endofdata'
                self.prelst = self.lst
                self.lst = []
                self.status = 1000
                return self.lexitem()

###                 # If nothing was collected, just stop iteration.
###                 if self.symbol is None and not self.lst and not self.prelst:
###                     raise StopIteration
###
###                 # Return the last collected lexical item.
###                 if self.symbol is None:
###                     self.symbol = 'skip'
###                 return self.lexitem()

            #----------------------------   unknown status
            else:
                raise NotImplementedError('Unknown status: {}'.format(self.status))

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


#-----------------------------------------------------------------------

if __name__ == '__main__':
    source = '// komentář'
    for e in Container(source):
        print(e)