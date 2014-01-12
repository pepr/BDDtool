#!python3
# -*- coding: utf-8 -*-
'''Lexical analysis for the Catch test sources.'''

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