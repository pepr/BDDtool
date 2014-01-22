#!python3
# -*- coding: utf-8 -*-
'''Lexical analysis for the xxx.feature source files.'''

import re

# The .feature files contain human-readable sentences. It is line oriented
# in the sense that each line has a specific meaning. The first words
# on the line determine a kind of the line. In some sense, each line
# can be viewed as a lexical token (with respect to the compiler theory).
# The first words of the line determine the symbol of the lexical token,
# the other part of the line captures the value (lexem) of the token.
#
# The following list of items contain the tuples where the first element
# captures a regular expression, the second element is the lex symbol identifier.
#
# The first words may have more forms (think or about more human languages
# or about various free language expressions where the alternatives improve
# readability of the text). The important subpaterns only are only described
# below. The related full patterns are constructed in the build_rex_closures()
# below.
rulesRex = [
    # Empty lines.
    (r'',                       'emptyline'),


    # Labels that identify portions via free text (inside comments
    # of the Catch test sources).
    (r'(User\s+)?Story:',       'story'),
    (r'Feature:',               'feature'),
    (r'Scenario:',              'scenario'),
    (r'Given:',                 'given'),
    (r'When:',                  'when'),
    (r'Then:',                  'then'),

    (r'Test:',                  'test_case'),
    (r'Sec(tion)?:',            'section'),

    # Czech equivalents.
    (r'(Uživatelský\s+)?Požadavek:', 'story'),
    (r'Rys:',                   'feature'),
    (r'Scénář:',                'scenario'),
    (r'Dáno:',                  'given'),
    (r'Když:',                  'when'),
    (r'Pak:',                   'then'),

]

#-----------------------------------------------------------------------

def build_rex_closures(pattern, lexsym):
    '''Builds the pair of closures for the regex pattern.'''

    def match_rex(line):
        # Actually returns a match object that can be interpreted
        # in a boolean context as True/False (matches/does not match).
        rex = re.compile(pattern, re.IGNORECASE)
        return rex.match(line)

    def result_rex(line):
        m = match_rex(line)             # see the match_rex() above
        lexem = m.group('lexem')        # lexem is always present
        if lexsym == 'emptyline':
            text = None                 # empty line whitespaces are in the lexem
        else:
            text = m.group('text')      # the matched text

        tags = None
        if lexsym in ('scenario', 'test_case'):
            tags = m.group('tags')

        return lexsym, lexem, text, tags

    return match_rex, result_rex

#-----------------------------------------------------------------------

def buildRegexMatchFunctions():
    '''Builds the list of (match_fn, result_fn) closures for regular expressions.'''

    # As a container can be iterated by several iterators, both the container
    # and the iterator must be passed (not captured inside the closures).
    # The rules are defined by the global one; hence, captured inside.
    functions = []

    for pat, lexsym in rulesRex:
        if lexsym == 'emptyline':
            pattern = r'^(?P<lexem>\s*)$'
        elif lexsym in ('scenario', 'test_case'):
            pattern = r'^\s*(?P<lexem>' + pat + \
                      r')\s*(?P<text>.*?)\s*(?P<tags>(\[\w+\])*)\s*$'
        else:
            pattern = r'^\s*(?P<lexem>' + pat + r')\s*(?P<text>.*?)\s*$'

        functions.append(build_rex_closures(pattern, lexsym))

    return functions

#-----------------------------------------------------------------------

class Iterator:
    '''Iterates over the Container and returns lexical elements.'''

    def __init__(self, container, startlineno):
        self.container = container
        self.lineno = startlineno

        self.lines = self.container.lines
        self.len = len(self.lines)

        self.status = 0         # of the finite automaton
        self.symbol = None
        self.lexem = None
        self.text = None
        self.tags = None        # for scenario/test

        self.regex_match_fns = buildRegexMatchFunctions()


    def __iter__(self):
        return self


    def notImplemented(self, msg=''):
        raise NotImplementedError('status={}: {!r}'.format(self.status, msg))


    def lextoken(self):
        '''Forms lexical token from the member variables.'''

        # Form the lexical token.
        token = (self.symbol, self.lexem, self.text, self.tags)

        # Warn if symbol was not recognized.
        if self.symbol is None:
            print('Warning: symbol not set for', token)

        # Reset the variables.
        self.symbol = None
        self.lexem = None
        self.text = None
        self.tags = None

        # Return the result.
        return token


    def expected(self, s):
        '''Forms error lexical token.'''

        # Form the lexical token.
        current = (self.symbol, ''.join(self.lst),
                   ''.join(self.prelst), self.post)
        token = ('error', '{!r} expected'.format(s),
                repr(current), None)

        # Reset the variables.
        self.symbol = None
        self.lst = []
        self.prelst = []
        self.post = None

        # Return the result.
        return token


    def __next__(self):
        '''Returns lexical tokens (symbol, lexem, text, tags).'''

        # Loop until the end of data.
        while self.status != 1000:

            # Get the next character or set the status for the end of data
            if self.lineno < self.len:
                line = self.lines[self.lineno]
                self.lineno += 1           # advanced to the next one
            else:
                # End of data.
                self.status = 800

            #============================   initial state, nothing known
            if self.status == 0:
                assert self.symbol is None
                for match_fn, result_fn in self.regex_match_fns:
                    if match_fn(line):
                        self.symbol, self.lexem, self.text, self.tags = result_fn(line)
                        return self.lextoken()

                # Other lines are considered just 'line'.
                self.symbol = 'line'
                self.lexem = line
                self.text = None
                self.tags = None

                return self.lextoken()

            #----------------------------   end of data
            elif self.status == 800:
                self.symbol = 'endofdata'
                self.lexem = ''
                self.text = ''
                self.tags = None
                self.status = 1000
                return self.lextoken()

            #----------------------------   unknown status
            else:
                raise NotImplementedError('Unknown status: {}'.format(self.status))

        raise StopIteration

#-----------------------------------------------------------------------

class Container:
    '''Iterable container for lexical parsing of the *.feature source.

    The source is passed as a multiline string, processed by lines.
    '''

    def __init__(self, source):
        # Warning: This is a spike solution
        if source == '':
            self.lines = []
        else:
            lines = source.split('\n')    # multiline split to list of lines
            self.lines = [line + '\n' for line in lines]    # adding newlines back


    def __iter__(self):
        return Iterator(self, 0)


#-----------------------------------------------------------------------

if __name__ == '__main__':
    import textwrap
    source = textwrap.dedent('''\
        Story: BDD oriented complex example

            As a normal user
            I want to capture this case that shows the way of prescribing my acceptance
            so that I am able to express my requirements without programming.

        Scenario: vectors can be sized and resized
             Given: A vector with some items
              When: more capacity is reserved
              Then: the capacity changes but not the size''')

    for e in Container(source):
        print(e)