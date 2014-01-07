#!python3

import re

class Element:
    '''Element recognition from the Catch xxx.h source files.'''

    # Pro detekci řádku se stručným popisem požadavku. Do testu byl opsán
    # jako C++ komentář.
    rexFeature = re.compile(r'''^//\s+(Feature|Požadavek)\s*:\s*
                                (?P<text>.+)$''',
                            re.IGNORECASE | re.VERBOSE)

    # Pro detekci prvního řádku s user story. Do testu byl opsán jako C++ komentář.
    rexUserStory = re.compile(r'^//\s+(User story)\s*:', re.IGNORECASE)

    # Pro detekci řádku s identifikací scénáře a pro extrakci textu.
    # Následující regulární výrazy pak detekují další součásti popisu
    # scénáře, které se transformují do podoby příslušných Catch sekcí.
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

    # Řádek uzavírající blok musí obsahovat jen pravou složenou závorku.
    rexRCurly =  re.compile(r'^\s*}')

    def __init__(self, fname, lineno, line):
        self.fname = fname      # původní zdrojový soubor
        self.lineno = lineno    # číslo řádku ve zdrojovém souboru
        self.line = line        # původní řádek

        self.type = None        # typ elementu
        self.text = None        # význačný text elementu
        self.tags = None        # nepovinný atributy elementu scenario

        # Řádek obsahující jen whitespace považujeme za prázdný
        # řádek ve významu oddělovače.
        if self.line.isspace():
            self.type = 'empty'
            self.text = ''   # reprezentací bude prázdný řetězec
            return

        # Řádek s Feature.
        m = self.rexFeature.search(line)
        if m:
            self.type = 'feature'
            self.text = m.group('text').rstrip()
            return

        # Řádek s User Story.
        m = self.rexUserStory.search(line)
        if m:
            self.type = 'userstory'
            self.text = line.rstrip()
            return

        # Řádek s identifikací scénáře. Další řádky s Given, When, Then
        # mají stejnou strukturu. Pocházejí z řetězcového literálu, takže
        # atribut naplníme hodnotou po odstranění escape \".
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

        # Pravá složená závorka uzavírající blok.
        m = self.rexRCurly.search(line)
        if m:
            self.type = 'rcurly'
            self.text = None
            return

        #--------------------------------------------------------------------
        # Prázdný řádek odpovídá situaci, kdy skončil soubor a další řádek
        # nebylo možno načíst. Neměl by nastávat, ale pro jistotu.
        if self.line == '':
            # Z pohledu řešeného problému to tedy není prázdný řádek
            # ve významu oddělovače.
            self.type = 'EOF'
            self.text = None
            return

        # Ostatní případy budeme považovat za řádek.
        self.type = 'line'
        self.text = line.rstrip()


    def __repr__(self):
        return repr((self.fname, self.lineno, self.type, self.text))


    def __str__(self):
        return self.line
