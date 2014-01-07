#!python3

import re

class Element:
    '''Element recognition from the Catch xxx.h source files.'''

    # The line with Feature: was included as a C++ comment.
    rexFeature = re.compile(r'''^//\s+(Feature|Požadavek)\s*:\s*
                                (?P<text>.+)$''',
                            re.IGNORECASE | re.VERBOSE)

    # First line of a User Story was included as a C++ comment.
    rexUserStory = re.compile(r'^//\s+(User story)\s*:', re.IGNORECASE)

    # Detection of the Catch test case and the sections. Notice that
    # the opening curly brace must be part of the line in this version.
    rexScenario = re.compile(r'''^\s*SCENARIO\("
                                 (?P<text>.+)
                                 "\)\s*{$''', re.VERBOSE)
    rexGiven = re.compile(r'''^\s*GIVEN\("
                              (?P<text>.+)
                              "\)\s*{$''', re.VERBOSE)
    rexWhen = re.compile(r'''^\s*WHEN\("
                             (?P<text>.+)
                             "\)\s*{$''', re.VERBOSE)
    rexThen = re.compile(r'''^\s*THEN\("
                             (?P<text>.+)
                             "\)\s*{$''', re.VERBOSE)

    # A block must be closed by the closing brace at a separate line..
    rexRCurly =  re.compile(r'^\s*}')

    def __init__(self, sourcenameinfo, lineno, line):
        self.sourcenameinfo = sourcenameinfo  # name of the source file or '<str>'
        self.lineno = lineno    # in the source
        self.line = line        # the line to be converted to the element

        self.type = None        # type of the element
        self.text = None        # the important text of the element
        self.tags = None        # optional tags of the scenario

        # A whitespaces-only line is considered empty (separator).
        if self.line.isspace():
            self.type = 'empty'
            self.text = ''      # representation of the empty line
            return

        # Recognition of the elements (see the related identifiers).
        m = self.rexFeature.search(line)
        if m:
            self.type = 'feature'
            self.text = m.group('text').rstrip()
            return

        m = self.rexUserStory.search(line)
        if m:
            self.type = 'userstory'
            self.text = line.rstrip()
            return

        # At the time of writing, only the doublequotes were escaped
        # in the sources. The string literals must be unescaped (no fancy
        # solution, yet).
        m = self.rexScenario.match(line)
        if m:
            self.type = 'scenario'
            self.text = m.group('text').rstrip().replace(r'\"', '"')
            return

        m = self.rexGiven.match(line)
        if m:
            self.type = 'given'
            self.text = m.group('text').rstrip().replace(r'\"', '"')
            return

        m = self.rexWhen.match(line)
        if m:
            self.type = 'when'
            self.text = m.group('text').rstrip().replace(r'\"', '"')
            return

        m = self.rexThen.match(line)
        if m:
            self.type = 'then'
            self.text = m.group('text').rstrip().replace(r'\"', '"')
            return

        # The right curly brace must be placed on a separate line
        # for this version.
        m = self.rexRCurly.search(line)
        if m:
            self.type = 'rcurly'
            self.text = None
            return

        # Other cases are just lines.
        self.type = 'line'
        self.text = line.rstrip()


    def __repr__(self):
        return repr((self.sourcenameinfo, self.lineno, self.type, self.text))


    def __str__(self):
        return self.line
