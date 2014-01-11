#!python3
# -*- coding: utf-8 -*-
'''Lexical analysis for the Catch test sources.'''

class Iterator:
    '''Iterates over the Container and returns lexical elements.'''

    def __init__(self, container, startpos):
        self.container = container
        self.pos = startpos

        self.source = self.container.source
        self.srclen = len(self.source)

        print(repr(self.source))
        print(repr(self.srclen))

        self.status = 0         # of the finite automaton
        self.symbol = None
        self.lexem = None
        self.lst = []
        self.prelst = []


    def __iter__(self):
        return self


    def __next__(self):
        '''Returns lexical items (symbol, lexem, pre, post).'''

        # Get the next character or set the status for the end of data
        if self.status != 888:
            raise StopIteration

        if self.pos < self.srclen:
            c = self.source[self.pos]
            self.lst.append(c)
            print(self.pos, self.lst)
            self.pos += 1               # advanced to the next one
        else:
            self.status = 888           # end of data


        #----------------------------   skipping the ignored chars
        if self.status == 0:
            print(self.status, c)
            if c == '/':
                self.status = 1
            else:
                raise NotImplementedError('status 0, char={!r}'.format(c))

        #----------------------------   possible start of a comment
        elif self.status == 1:
            print(self.status, c)
            if c == '/':
                # The // comment recognized.
                self.prelst.extend(self.lst[:-2])
                self.symbol = 'comment'
                self.lst = []
                self.status = 2

        #----------------------------   end of data
        elif self.status == 888:
            # Return the last collected lexical item.
            return (self.symbol, ''.join(self.lst), ''.join(self.prelst))

        #----------------------------   unknown status
        else:
            print(self.status)
            raise NotImplementedError('Unknown status: {}'.format(self.status))

        print(self.pos, self.srclen, repr(c))

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

