#!python3

import re

class Element:
    '''Rozpoznané Elementy dokumentu odpovídající řádkům zdrojového textu.'''

    # Nejdříve regulární výrazy pro elementy z xxx.feature souboru.
    #
    # Pro detekci řádku se stručným popisem požadavku.
    rexFeature = re.compile('''^\s*(Feature|Požadavek)\s*:\s*
                                   (?P<text>.+)$''',
                             re.IGNORECASE | re.VERBOSE)

    # Pro detekci prvního řádku s user story.
    rexUserStory = re.compile('^\s*(User story)\s*:', re.IGNORECASE)

    # Pro detekci řádku s identifikací scénáře a pro extrakci textu.
    # Následující regulární výrazy pak detekují další součásti popisu
    # scénáře, které se transformují do podoby příslušných Catch sekcí.
    rexScenario = re.compile('''^\s*(Scenario|Example|Scénář|Příklad)\s*:\s*
                                    (?P<text>.+)$''',
                             re.IGNORECASE | re.VERBOSE)
    rexGiven = re.compile('''^\s*(Given|Dáno)\s*:\s*
                                 (?P<text>.+)\s*$''',
                             re.IGNORECASE | re.VERBOSE)
    rexWhen = re.compile('''^\s*(When|Když)\s*:\s*
                                (?P<text>.+)\s*$''',
                             re.IGNORECASE | re.VERBOSE)
    rexThen = re.compile('''^\s*(Then|Pak)\s*:\s*
                                (?P<text>.+)\s*$''',
                             re.IGNORECASE | re.VERBOSE)

    # Odpovídající regulární výrazy pro parsing exitujícího generovaného
    # testu v xxx.h souborech. Regulární výrazy budou mít předponu rexTest.
    #
    # Pro detekci řádku se stručným popisem požadavku. Do testu byl opsán
    # jako C++ komentář.
    rexTestFeature = re.compile('''^//\s+(Feature|Požadavek)\s*:\s*
                                         (?P<text>.+)$''',
                                re.IGNORECASE | re.VERBOSE)

    # Pro detekci prvního řádku s user story. Do testu byl opsán jako C++ komentář.
    rexTestUserStory = re.compile('^//\s+(User story)\s*:', re.IGNORECASE)

    # Pro detekci řádku s identifikací scénáře a pro extrakci textu.
    # Následující regulární výrazy pak detekují další součásti popisu
    # scénáře, které se transformují do podoby příslušných Catch sekcí.
    rexTestScenario = re.compile('''^\s*SCENARIO\("
                                    (?P<text>.+)
                                    "\)\s*{$''', re.VERBOSE)
    rexTestGiven = re.compile('''^\s*GIVEN\("
                                 (?P<text>.+)
                                 "\)\s*{$''', re.VERBOSE)
    rexTestWhen = re.compile('''^\s*WHEN\("
                                 (?P<text>.+)
                                 "\)\s*{$''', re.VERBOSE)
    rexTestThen = re.compile('''^\s*THEN\("
                                 (?P<text>.+)
                                 "\)\s*{$''', re.VERBOSE)

    # Řádek uzavírající blok musí obsahovat jen pravou složenou závorku.
    rexRCurly =  re.compile('^\s*}')

    def __init__(self, fname, lineno, line):
        self.fname = fname      # původní zdrojový soubor
        self.lineno = lineno    # číslo řádku ve zdrojovém souboru
        self.line = line        # původní řádek

        self.type = None        # typ elementu
        self.attrib = None      # init -- atributy elementu (význam dle typu)

        # Řádek obsahující jen whitespace považujeme za prázdný
        # řádek ve významu oddělovače.
        if self.line.isspace():
            self.type = 'empty'
            self.attrib = ''   # reprezentací bude prázdný řetězec
            return

        # Řádek s Feature.
        m = self.rexFeature.search(line)
        if m:
            self.type = 'feature'
            self.attrib = m.group('text').rstrip()
            return

        # Řádek s User Story.
        m = self.rexUserStory.search(line)
        if m:
            self.type = 'userstory'
            self.attrib = line.rstrip()
            return

        # Řádek s identifikací scénáře. Další řádky s Given, When, Then
        # mají stejnou strukturu.
        m = self.rexScenario.match(line)
        if m:
            self.type = 'scenario'
            self.attrib = m.group('text').rstrip()
            return

        m = self.rexGiven.match(line)
        if m:
            self.type = 'given'
            self.attrib = m.group('text').rstrip()
            return

        m = self.rexWhen.match(line)
        if m:
            self.type = 'when'
            self.attrib = m.group('text').rstrip()
            return

        m = self.rexThen.match(line)
        if m:
            self.type = 'then'
            self.attrib = m.group('text').rstrip()
            return

        #--------------------------------------------------------------------
        # Odpovídající řádky ze souboru testu.
        #
        # Řádek s Feature.
        m = self.rexTestFeature.search(line)
        if m:
            self.type = 'feature'
            self.attrib = m.group('text').rstrip()
            return

        # Řádek s User Story.
        m = self.rexTestUserStory.search(line)
        if m:
            self.type = 'userstory'
            self.attrib = line.rstrip()
            return

        # Řádek s identifikací scénáře. Další řádky s Given, When, Then
        # mají stejnou strukturu. Pocházejí z řetězcového literálu, takže
        # atribut naplníme hodnotou po odstranění escape \".
        m = self.rexTestScenario.match(line)
        if m:
            self.type = 'scenario'
            self.attrib = m.group('text').rstrip().replace(r'\"', '"')
            return

        m = self.rexTestGiven.match(line)
        if m:
            self.type = 'given'
            self.attrib = m.group('text').rstrip().replace(r'\"', '"')
            return

        m = self.rexTestWhen.match(line)
        if m:
            self.type = 'when'
            self.attrib = m.group('text').rstrip().replace(r'\"', '"')
            return

        m = self.rexTestThen.match(line)
        if m:
            self.type = 'then'
            self.attrib = m.group('text').rstrip().replace(r'\"', '"')
            return

        # Pravá složená závorka uzavírající blok.
        m = self.rexRCurly.search(line)
        if m:
            self.type = 'rcurly'
            self.attrib = None
            return

        #--------------------------------------------------------------------
        # Prázdný řádek odpovídá situaci, kdy skončil soubor a další řádek
        # nebylo možno načíst. Neměl by nastávat, ale pro jistotu.
        if self.line == '':
            # Z pohledu řešeného problému to tedy není prázdný řádek
            # ve významu oddělovače.
            self.type = 'EOF'
            self.attrib = None
            return

        # Ostatní případy budeme považovat za řádek.
        self.type = 'line'
        self.attrib = line.rstrip()


    def __repr__(self):
        return repr((self.fname, self.lineno, self.type, self.attrib))


    def __str__(self):
        return self.line
