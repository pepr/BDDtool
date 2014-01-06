#!python3

import docelement
import os

class Feature:
    '''Třída s parserem pro rozklad xxx.feature a odpovídajícího xxx.h.'''

    def __init__(self, featurefname, tests_dir, log_dir):
        self.identifier = None  # řetězcová identifikace se zjistí až po parse()
        self.featurefname = featurefname        # jméno .feature souboru
        self.tests_dir = tests_dir              # adresář pro soubory testů
        self.log_dir = log_dir                  # adresář pro log soubory

        # Odvodíme holé jméno (symbolické, bez přípony), jméno log souboru
        # a jméno souboru s testy.
        self.feature_bare_name = os.path.basename(self.featurefname)
        self.name, ext = os.path.splitext(self.feature_bare_name)
        self.test_bare_name = self.name + '.h'

        self.logfname = os.path.join(self.log_dir, self.name  + '.log')
        self.testfname = os.path.join(self.tests_dir, self.test_bare_name)

        # Objekt log souboru.
        self.flog = None

        self.feature_lst = None # seznam elementů z .feature
        self.h_lst = None       # seznam elementů z .h

        self.info_files = []    # info pro zobrazování zpracovaných souborů


    def id(self):
        '''Vrací řetězcovou identifikaci feature objektu.'''
        assert self.identifier is not None
        return self.identifier


    def openLogFile(self):
        assert self.flog is None
        self.flog = open(self.logfname, 'w', encoding='utf-8')


    def closeLogFile(self):
        self.flog.close()
        self.flog = None


    def loadFeatureElementList(self):
        '''Načte elementy z .feature do členského seznamu.'''

        self.feature_lst = []
        with open(self.featurefname,  encoding='utf-8') as fin:

            # Zpracujeme všechny řádky parserem.
            for lineno, line in enumerate(fin, 1):
                elem = docelement.Element(self.feature_bare_name, lineno, line)
                self.feature_lst.append(elem)
                self.flog.write(repr(elem) + '\n')

            # Přidáme informaci o dotčených souborech.
            self.info_files.append('r ' + self.featurefname)
            self.info_files.append('w ' + self.logfname)

        # Najdeme element typu 'feature' a získáme identifikaci. Nemusí být uvedena,
        # takže inicializujeme na prázdný řetězec.
        self.identifier = ''
        for elem in self.feature_lst:
            if elem.type == 'feature':
                self.identifier = elem.attrib
                break



    def loadTestElementList(self):
        '''Načte elementy z .h do členského seznamu.'''

        self.h_lst = []
        if os.path.isfile(self.testfname):
            with open(self.testfname,  encoding='utf-8') as fin:

                # Zpracujeme všechny řádky parserem.
                for lineno, line in enumerate(fin, 1):
                    elem = docelement.Element(self.test_bare_name, lineno, line)
                    self.feature_lst.append(elem)
                    self.flog.write(repr(elem) + '\n')

                # Přidáme informaci o dotčených souborech.
                self.info_files.append('r ' + self.testfname)
                self.info_files.append('w ' + self.logfname)


    def parse(self):
        '''Spouštěč jednotlivých fází parseru.'''

        self.openLogFile()
        self.loadFeatureElementList()
        self.flog.write('-' * 70 + '\n')
        self.loadTestElementList()
        self.closeLogFile()

        return '\n\t'.join(self.info_files)
