#!python3
"""Lexical analysis for the xxx.feature source files.
"""

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
    (r'emptyline dummy pat.',   'emptyline'),


    # Labels that identify portions via free text (inside comments
    # of the Catch test sources).
    (r'(User\s+)?Story:',       'story'),
    (r'Feature:',               'feature'),
    (r'Scenario:',              'scenario'),
    (r'Given:',                 'given'),
    (r'When:',                  'when'),
    (r'Then:',                  'then'),
    (r'And:',                   'and'),

    (r'Test:',                  'test_case'),
    (r'Sec(tion)?:',            'section'),

    # Czech equivalents.
    (r'(Uživatelský\s+)?Požadavek:', 'story'),
    (r'Rys:',                   'feature'),
    (r'Scénář:',                'scenario'),
    (r'Dáno:',                  'given'),
    (r'Když:',                  'when'),
    (r'Pak:',                   'then'),
    (r'a:',                     'and'),

]

#-----------------------------------------------------------------------

def build_rex_closures(pattern, lexsym):
    """Builds the pair of closures for the regex pattern.
    """

    def match_rex(line):
        # Actually returns a match object that can be interpreted
        # in a boolean context as True/False (matches/does not match).
        rex = re.compile(pattern, re.IGNORECASE)
        return rex.match(line)

    def result_rex(line):
        m = match_rex(line)             # see the match_rex() above

        text = ''
        if 'text' in m.groupdict():
            text = m.group('text')      # the matched text

        tags = None
        if lexsym in ('scenario', 'test_case'):
            tags = m.group('tags')

        ##print( (lexsym, text, tags) )
        return lexsym, text, tags

    return match_rex, result_rex

#-----------------------------------------------------------------------

def buildRegexMatchFunctions():
    """Builds the list of (match_fn, result_fn) closures for regular expressions.
    """
    # As a container can be iterated by several iterators, both the container
    # and the iterator must be passed (not captured inside the closures).
    # The rules are defined by the global one; hence, captured inside.
    functions = []

    for pat, lexsym in rulesRex:
        if lexsym == 'emptyline':
            pattern = r'^\s*$'
        elif lexsym in ('scenario', 'test_case'):
            pattern = r'^\s*' + pat + \
                      r'\s*(?P<text>.*?)\s*(?P<tags>(\[\w+\])*)\s*$'
        else:
            pattern = r'^\s*' + pat + r'\s*(?P<text>.*?)\s*$'

        functions.append(build_rex_closures(pattern, lexsym))

    return functions

#-----------------------------------------------------------------------

class Iterator:
    """Iterates over the Container and returns lexical elements.
    """

    def __init__(self, container, startlineno):
        self.container = container
        self.lineno = startlineno

        self.lines = self.container.lines
        self.len = len(self.lines)
        self.source_name = self.container.source_name

        self.status = 0         # of the finite automaton
        self.symbol = None
        self.value = None
        self.lexem = None
        self.tags = None        # for scenario/test

        self.regex_match_fns = buildRegexMatchFunctions()


    def __iter__(self):
        return self


    def notImplemented(self, msg=''):
        raise NotImplementedError('status={}: {!r}'.format(self.status, msg))


    def lextoken(self):
        """Forms lexical token from the member variables.
        """

        # Form the lexical token.
        tags = self.tags if self.tags else None
        token = (self.symbol, self.value, self.lexem, tags)

        # Warn if symbol was not recognized.
        if self.symbol is None:
            print('Warning: symbol not set for', token)

        # Reset the variables.
        self.symbol = None
        self.lexem = None
        self.value = None
        self.tags = None

        # Return the result.
        return token


    def expected(self, s):
        """Forms error lexical token.
        """

        # Form the lexical token.
        current = (self.symbol, ''.join(self.lst),
                   ''.join(self.prelst), self.post)
        source_name = self.source_name
        line_no = self.lineno
        token = ('error', '{!r}, {}: {!r} expected'.format(
                    source_name, line_no, s),
                repr(current), None)

        # Reset the variables.
        self.symbol = None
        self.lst = []
        self.prelst = []
        self.post = None

        # Return the result.
        return token


    def __next__(self):
        """Returns lexical tokens (symbol, lexem, text, tags).
        """
        # Loop until the end of data.
        while self.status != 1000:

            # Get the next character or set the status for the end of data
            if self.lineno < self.len:
                line = self.lines[self.lineno]
                self.lexem = line       # whole line is the lexem
                self.lineno += 1        # advanced to the next one
            else:
                # End of data.
                self.status = 800

            #============================   initial state, nothing known
            if self.status == 0:
                assert self.symbol is None
                for match_fn, result_fn in self.regex_match_fns:
                    if match_fn(line):
                        self.symbol, self.value, self.tags = result_fn(line)
                        return self.lextoken()

                # Other lines are considered just 'line'.
                self.symbol = 'line'
                self.value = line.rstrip()

                return self.lextoken()

            #----------------------------   end of data
            elif self.status == 800:
                self.symbol = '$'
                self.status = 1000
                return self.lextoken()

            #----------------------------   unknown status
            else:
                raise NotImplementedError('Unknown status: {}'.format(self.status))

        raise StopIteration

#-----------------------------------------------------------------------

class Container:
    """Iterable container for lexical parsing of the *.feature source.

    The source is passed or as a multiline string, or as an open file,
    processed by lines.
    """

    def __init__(self, source):
        if hasattr(source, 'readlines'):
            # It is a file object opened for reading lines in text mode.
            self.lines = source.readlines()
            self.source_name = source.name      # filename
        elif source == '':
            # It is an empty string.
            self.lines = []
            self.source_name = '<str>'
        else:
            # It is a multiline string.
            lines = source.split('\n')    # multiline split to list of lines
            self.lines = [line + '\n' for line in lines[:-1]]    # adding newlines back
            self.lines.append(lines[-1])
            self.source_name = '<str>'


    def __iter__(self):
        return Iterator(self, 0)


#-----------------------------------------------------------------------

if __name__ == '__main__':
    import textwrap
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

    for e in Container(source):
        print(e)