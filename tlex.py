#!python3
"""Lexical analysis for the Catch test sources.
"""

import re

# The Catch-defined identifiers are considered keywords for this purpose.
# The following list of items contain the tuples with the following
# meaning...
#
# The first element captures an exact string pattern (not a regular expression),
# the second element is the lex symbol identifier.
rulesStr = [
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

# The BDD text Story/Feature with title that was generated into comments
# is recognized as a special token when postprocessint a comment token.
# If recognized, the 'comment' is changed to 'story' or 'feature'.
# The matched label may have more forms (think about more human languages
# in the comment). The subpaterns for label are only described here.
# The related full patterns are constructed in the buildRegexMatchFunctions()
# below.
rulesRex = [
    # Labels that identify portions via free text (inside comments
    # of the Catch test sources).
    (r'(User\s+)?Story',    'story'),
    (r'Feature',            'feature'),

    # Czech equivalents.
    (r'(Uživatelský\s+)?Požadavek',  'story'),
    (r'Rys',                         'feature'),
]

#-----------------------------------------------------------------------

def build_str_closures(s, lexid, iterator):
    """Builds the pair of closures for recognizing exact strings.
    """
    def match_str(iterator):
        return iterator.source.startswith(s, iterator.pos)

    def result_str(iterator):
        return lexid, s, iterator.pos + len(s)

    return (match_str, result_str)

#-----------------------------------------------------------------------

def build_rex_closures(pattern, lexsym):
    """Builds the pair of closures for the regex pattern.
    """
    # Unlike the above build_str_closures(), it works directly with a string
    # variable and positions -- i.e. can be used independently on Container/Iterator
    # of the lexical analyzer. The result function also returns a tuple
    # with more elements.

    def match_rex(source, pos):
        # Actually returns a match object that can be interpreted
        # in a boolean context as True/False (matches/does not match).
        rex = re.compile(pattern, re.IGNORECASE)
        return rex.match(source[pos:])

    def result_rex(source, pos):
        m = match_rex(source, pos)      # see the match_rex() above
        text = m.group('text')          # the matched text
        return lexsym, text

    return (match_rex, result_rex)

#-----------------------------------------------------------------------

def buildExactStrMatchFunctions(iterator):
    """Builds the list of (match_fn, result_fn) closures for exact strings.
    """
    functions = []

    for s, lexid in rulesStr:
        functions.append(build_str_closures(s, lexid, iterator))

    return functions

#-----------------------------------------------------------------------

def buildRegexMatchFunctions():
    """Builds the list of (match_fn, result_fn) closures for regular expressions.
    """
    functions = []

    for pat, lexid in rulesRex:
        # Variant for a single line.
        pattern = r'\s*' + pat + r':\s*(?P<text>.+?)\s*$'
        functions.append(build_rex_closures(pattern, lexid))

        # Variant for a multi line.
        pattern = r'\s*' + pat + r':\s*(?P<text>.+?)\s*\n'
        functions.append(build_rex_closures(pattern, lexid))

    return functions

#-----------------------------------------------------------------------

class Iterator:
    """Iterates over the Container and returns lexical elements.
    """
    def __init__(self, container, startpos):
        self.container = container
        self.pos = startpos

        self.source = self.container.source
        self.srclen = len(self.container.source)
        self.source_name = self.container.source_name
        self.lineno = 1

        self.status = 0         # of the finite automaton
        self.symbol = None
        self.valuelst = []
        self.lexemlst = []
        self.extra_info = None

        self.exact_str_match_fns = buildExactStrMatchFunctions(self)
        self.regex_match_fns = buildRegexMatchFunctions()


    def __iter__(self):
        return self


    def notImplemented(self, msg=''):
        source_name = self.source_name
        line_no = self.lineno
        raise NotImplementedError(('status={}: {!r}\n'
                                   'line no. {}, source {!r}').format(
                                       self.status, msg,
                                       line_no, source_name))


    def lextoken(self):
        """Forms lexical token from the member variables.
        """
        # Form the lexical token: (symbol, value, lexem, extra_info)
        if self.symbol in ('stringlit', 'newline', 'comment'):
            # Here the value should always be a string, even if nothing was
            # collected. The reason is that the value may be further processed
            # and the None would cause complications.
            value = ''.join(self.valuelst) if self.valuelst else ''
        else:
            value = ''.join(self.valuelst) if self.valuelst else None

        token = (self.symbol, value,
                 ''.join(self.lexemlst) if self.lexemlst else None,
                 self.extra_info)

        # Warn if symbol was not recognized.
        if self.symbol is None:
            print('Warning: symbol not set for', token)

        # Reset the variables.
        self.symbol = None
        self.valuelst = []
        self.lexemlst = []
        self.extra_info = None

        # Return the result.
        return token


    def expected(self, s):
        """Forms error lexical token.
        """
        # Form the lexical token.
        current = self.lextoken()

        source_name = self.source_name
        line_no = self.lineno
        error_token = ('error', '{!r}, {}: {!r} expected'.format(
                                 source_name, line_no, s),
                        repr(current), None)


        # Return the result.
        return error_token


    def comment_or_feature(self):
        """Checks and possibly converts the token from comment to feature/story.
        """
        assert self.symbol == 'comment'
        value = ''.join(self.valuelst)

        for match_fn, result_fn in self.regex_match_fns:
            pos = 0
            if match_fn(value, pos):
                symbol, new_value = result_fn(value, pos)
                assert symbol == 'story' or symbol == 'feature'
                assert self.symbol == 'comment'

                # Change the symbol identifier and replace the value.
                self.symbol = symbol
                self.valuelst = [ new_value ]

                # Return the token.
                return self.lextoken()

        # Nothing special recognized. Returned as 'comment' token.
        return self.lextoken()


    def add_to_lexem(self, c):
        """Add the char to the lexem, update the position.
        """
        c = self.source[self.pos]
        self.lexemlst.append(c)
        self.pos += 1           # advanced to the next one
        if c == '\n':
            self.lineno += 1    # line counter for error messages


    def back_from_lexem(self):
        """Back from the lexem, update the position.
        """
        c = self.lexemlst[-1]
        del self.lexemlst[-1]
        self.pos -= 1           # back to the previous one
        if c == '\n':
            self.lineno -= 1    # line counter for error messages
        return c


    def __next__(self):
        """Returns lexical tokens (symbol, lexem, pre, post).
        """
        # Loop until the end of data.
        while self.status != 1000:

            # Get the next character or set the status for the end of data
            if self.pos < self.srclen:
                c = self.source[self.pos]
                self.add_to_lexem(c)
            else:
                # End of data, but the previous element may not be
                # entirely collected/finalized.
                if self.status == 3:    # waiting for end of comment */
                    # The state is not final, return the error
                    error = self.expected('*/')
                    self.status = 800
                    return error
                elif self.status == 2:  # empty // comment just before end of data
                    token = self.comment_or_feature()
                    self.status = 800
                    return token
                elif self.status == 5:  # closing dquote of "literal" missing
                    error = self.expected('"')
                    self.status = 800
                    return error
                elif self.status == 8:  # assignment followed by $
                    self.symbol = 'assignment'
                    self.status = 800
                    return self.lextoken()
                elif self.status == 9:  # a number followed by $
                    self.status = 800
                    return self.lextoken()
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
                    self.symbol = 'newline'
                    return self.lextoken()
                elif c == '"':          # string literal started
                    self.symbol = 'stringlit'
                    self.status = 5
                elif c == '(':          # left parenthesis
                    self.symbol = 'lpar'
                    return self.lextoken()
                elif c == ')':          # right parenthesis
                    self.symbol = 'rpar'
                    return self.lextoken()
                elif c == '{':          # left brace
                    self.symbol = 'lbrace'
                    return self.lextoken()
                elif c == '}':          # right brace
                    self.symbol = 'rbrace'
                    return self.lextoken()
                elif c == ',':          # comma
                    self.symbol = 'comma'
                    return self.lextoken()
                elif c == ':':          # colon
                    self.symbol = 'colon'
                    return self.lextoken()
                elif c == ';':          # semicolon
                    self.symbol = 'semic'
                    return self.lextoken()
                elif c == '#':          # hash like in #include
                    self.symbol = 'hash'
                    return self.lextoken()
                elif c == '=':          # assignment or eq operator
                    self.status = 8
                else:
                    # Loop through the closure pairs to find the lex token.
                    # When the match is found, return early.
                    self.back_from_lexem()

                    for match_fn, result_fn in self.exact_str_match_fns:
                        if match_fn(self):
                            symbol, lexem, newpos = result_fn(self)
                            self.pos = newpos
                            self.symbol = symbol
                            self.lexemlst.append(lexem)
                            return self.lextoken()

                    # No symbol found in the table. Possibly an identifier.
                    if c.isalpha() or c == '_':
                        self.symbol = 'identifier'
                        self.valuelst.append(c)
                        self.status = 7
                    elif c.isdigit():
                        self.symbol = 'num'
                        self.valuelst.append(c)
                        self.status = 9
                    else:
                       self.notImplemented(c)

            #----------------------------   possible start of a comment
            elif self.status == 1:
                if c == '/':
                    # The C++ // comment recognized.
                    self.symbol = 'comment'
                    self.status = 2     # collect content of // comment
                elif c == '*':
                    # The C /* comment started.
                    self.symbol = 'comment'
                    self.status = 3     # collect content of the  /* comment */
                else:
                    self.notImplemented(c)

            #----------------------------   comment till the end of line
            elif self.status == 2:
                if c == '\n':
                    # End of line -- end of the // comment. It could be
                    # the Story or Feature inside. Return or 'comment', or
                    # 'story', or 'feature'.
                    token = self.comment_or_feature()
                    self.status = 0
                    return token

                # All other characters are consumed as the comment value.
                self.valuelst.append(c)

            #----------------------------   collecting comment till */
            elif self.status == 3:
                if c == '*':
                    self.status = 4     # possibly end of C comment
                else:
                    # Add other characters to the comment value.
                    self.valuelst.append(c)

            #----------------------------   comment */ closed
            elif self.status == 4:
                if c == '/':
                    # Here the self.post will be filled with the '*/'.
                    # This is important for the text reconstruction.
                    self.status = 0
                    return self.comment_or_feature()
                elif c == '*':
                    self.valuelst.append('*') # previous extra star to the value
                else:
                    self.valuelst.append('*') # previous extra star to the value
                    self.valuelst.append(c)
                    self.status = 3     # collecting other chars

            #----------------------------   collecting string literal chars
            elif self.status == 5:
                if c == '"':
                    # String literal finished.
                    self.status = 0
                    return self.lextoken()
                elif c == '\\':         # backlash starts an escape sequence
                    self.status = 6

                # If not '"' then collected as a part of the literal value.
                self.valuelst.append(c)

            #----------------------------   the char after the escape
            elif self.status == 6:
                # Any char after esc. Now back to collecting other characters
                # of the string literal.
                self.valuelst.append(c)
                self.status = 5

            #----------------------------   collecting identifier characters
            elif self.status == 7:
                if c.isalnum() or c == '_':
                    self.valuelst.append(c)
                else:
                    self.back_from_lexem()
                    self.status = 0
                    return self.lextoken()      # the identifier

            #----------------------------   assignment (=) or eq operator (==)
            elif self.status == 8:
                if c == '=':
                    self.symbol = 'eq'
                    self.status = 0
                    return self.lextoken()
                else:
                    self.back_from_lexem()
                    self.status = 0
                    self.symbol = 'assignment'
                    return self.lextoken()

            #----------------------------   a number
            elif self.status == 9:
                if c.isdigit():
                    self.valuelst.append(c)
                else:
                    self.back_from_lexem()
                    self.status = 0
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
    """Iterable container for lexical parsing of the Catch-test source.

    The source is passed as a multiline string.
    """

    def __init__(self, source):
        if hasattr(source, 'read'):
            # It is a file object opened for reading lines in text mode.
            self.source = source.read()
            self.source_name = source.name      # filename
        elif source == '':
            # It is an empty string.
            self.source = ''
            self.source_name = '<str>'
        else:
            # It is a multiline string.
            self.source = source
            self.source_name = '<str>'


    def __iter__(self):
        return Iterator(self, 0)


#-----------------------------------------------------------------------

if __name__ == '__main__':
    source = '// komentář'
    for e in Container(source):
        print(e)