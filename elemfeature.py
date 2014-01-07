#!python3

import re

class Element:
    '''Element recognition from the xxx.feature source files.'''

    # Regular expressions for detecting the related elements.
    rexFeature = re.compile(r'''^\s*(Feature|Požadavek)\s*:\s*
                                (?P<text>.+)$''',
                             re.IGNORECASE | re.VERBOSE)

    rexUserStory = re.compile('^\s*(User story)\s*:', re.IGNORECASE)

    # The Scenario may contain [tags], the other only a text.
    rexScenario = re.compile(r'''^\s*(Scenario|Example|Scénář|Příklad)\s*:\s*
                                 (?P<text>.+?)\s*
                                 (?P<tags>(\[\w+\])*)
                                 \s*$''',
                             re.IGNORECASE | re.VERBOSE)
    rexGiven = re.compile(r'''^\s*(Given|Dáno)\s*:\s*
                              (?P<text>.+)\s*$''',
                             re.IGNORECASE | re.VERBOSE)
    rexWhen = re.compile(r'''^\s*(When|Když)\s*:\s*
                             (?P<text>.+)\s*$''',
                             re.IGNORECASE | re.VERBOSE)
    rexThen = re.compile(r'''^\s*(Then|Pak)\s*:\s*
                             (?P<text>.+)\s*$''',
                             re.IGNORECASE | re.VERBOSE)


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

        m = self.rexScenario.match(line)
        if m:
            self.type = 'scenario'
            self.text = m.group('text').rstrip()
            self.tags = m.group('tags')
            return

        m = self.rexGiven.match(line)
        if m:
            self.type = 'given'
            self.text = m.group('text').rstrip()
            return

        m = self.rexWhen.match(line)
        if m:
            self.type = 'when'
            self.text = m.group('text').rstrip()
            return

        m = self.rexThen.match(line)
        if m:
            self.type = 'then'
            self.text = m.group('text').rstrip()
            return


        # Other cases are just lines.
        self.type = 'line'
        self.text = line.rstrip()


    def __repr__(self):
        return repr((self.sourcenameinfo, self.lineno, self.type, self.text))


    def __str__(self):
        return self.line
