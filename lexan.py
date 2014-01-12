#!python3
# -*- coding: utf-8 -*-
'''Lexical analysis for the Catch test sources.'''


# The Catch-defined identifiers are considered keywords for this purpose.
# Also the BDD text that were generated into comments are considered
# keywords for the purpose -- that is because we want to reconstruct
# the *.feature file information from the comment. The matched keyword
# may have more forms (think about more human languages used for keywords
# in comments).
#
# The following list of items contain the tuples with the following
# meaning...
#
# The first element determines the method of recognition of the item:
# 0 - exact char sequence, 1 - regular character pattern.
#
# The second element captures a pattern depending on the on the first element.
# Or it is the exact string, or it is a regular expression pattern.
#
# The third element is the lex symbol identifier.
#
# The following rules are evaluated in this order. The order can
# be important sometimes.
#
rules = [
    (0, '(',            'lpar'),
    (0, ')',            'rpar'),
    (0, '{',            'lbrace'),
    (0, '}',            'rbrace'),
    (0, '"',            'dquote'),
    (0, '\n',           'newline'),

    # Catch identifiers.
    (0, 'SCENARIO',     'scenario'),
    (0, 'GIVEN',        'given'),
    (0, 'WHEN',         'when'),
    (0, 'THEN',         'then'),
    (0, 'TEST_CASE',    'test_case'),
    (0, 'SECTION',      'section'),

    # Labels that identify portions via free text.
    (1, r'(?i)(User\s+)?Story',            'lab_story'),
    (1, r'(?i)(Uživatelský\s+)?Požadavek', 'lab_story'),
    (1, r'(?i)Feature',         'lab_feature'),
    (1, r'(?i)Rys',             'lab_feature'),

    # Other things.
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
        while self.status != 888:

            # Get the next character or set the status for the end of data
            if self.pos < self.srclen:
                c = self.source[self.pos]
                self.lst.append(c)
                self.pos += 1           # advanced to the next one
            else:
                # End of data. If the state is not final, return
                # the 'error' item.
                error = None
                if self.status == 3:    # waiting for end of comment */
                    error = self.expected('*/')

                self.status = 888       # end of data
                if error:
                    return error

            #============================   initial state, nothing known
            if self.status == 0:
                assert self.symbol is None
                if c == '/':            # comment?
                    self.status = 1
                elif c in ' \t':
                    pass                # skip tabs and spaces
                elif c == '\n':
                    assert self.symbol is None
                    self.symbol = 'emptyline'
                    return self.lexitem()
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

            #----------------------------   end of data
            elif self.status == 888:
                # If nothing was collected, just stop iteration.
                if self.symbol is None and not self.lst and not self.prelst:
                    raise StopIteration

                # Return the last collected lexical item.
                if self.symbol is None:
                    self.symbol = 'skip'
                return self.lexitem()

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