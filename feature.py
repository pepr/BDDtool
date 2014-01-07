#!python3

import elemfeature
import elemcpp
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

        self.msg_lst = []    # info pro zobrazování zpracovaných souborů


    def id(self):
        '''Vrací řetězcovou identifikaci feature objektu.'''
        assert self.identifier is not None
        return self.identifier


    def openLogFile(self):
        assert self.flog is None
        self.flog = open(self.logfname, 'w', encoding='utf-8')
        self.msg_lst.append('w ' + self.logfname)


    def closeLogFile(self):
        self.flog.close()
        self.flog = None


    def loadFeatureElementList(self):
        '''Načte elementy z .feature do členského seznamu.'''

        self.feature_lst = []
        with open(self.featurefname,  encoding='utf-8') as fin:

            # Zpracujeme všechny řádky parserem.
            for lineno, line in enumerate(fin, 1):
                elem = elemfeature.Element(self.feature_bare_name, lineno, line)
                self.feature_lst.append(elem)
                self.flog.write(repr(elem) + '\n')

            # Přidáme informaci o dotčených souborech.
            self.msg_lst.append('r ' + self.featurefname)

        # Najdeme element typu 'feature' a získáme identifikaci. Nemusí být uvedena,
        # takže inicializujeme na prázdný řetězec.
        self.identifier = ''
        for elem in self.feature_lst:
            if elem.type == 'feature':
                self.identifier = elem.text
                break



    def loadTestElementList(self):
        '''Načte elementy z .h do členského seznamu.'''

        self.h_lst = []
        if os.path.isfile(self.testfname):
            with open(self.testfname,  encoding='utf-8') as fin:

                # Zpracujeme všechny řádky parserem.
                for lineno, line in enumerate(fin, 1):
                    elem = elemcpp.Element(self.test_bare_name, lineno, line)
                    self.feature_lst.append(elem)
                    self.flog.write(repr(elem) + '\n')

                # Přidáme informaci o dotčených souborech.
                self.msg_lst.append('r ' + self.testfname)

    def scenario(self, lst, level):
        '''Vrací C++ obraz scénáře pro Catch unit testing.'''
        result = []
        if len(lst) > 0:
            elem = lst[0]
            assert elem.type == 'scenario'
            identifier = elem.text.replace('"', r'\"')
            indent = ' ' * 4 * level
            result.append('{}SCENARIO("{}") {{'.format(indent, identifier))
            result.append(self.given(lst[1:], level + 1))
            result.append(indent + '}')

        return '\n'.join(result)


    def given(self, lst, level):
        '''Vrací obraz sekce GIVEN pro Catch unit testing.'''
        result = []
        if len(lst) > 0:
            elem = lst[0]
            assert elem.type == 'given'
            identifier = elem.text.replace('"', r'\"')
            indent = ' ' * 4 * level
            result.append('{}GIVEN("{}") {{'.format(indent, identifier))
            result.append(self.when(lst[1:], level + 1))
            result.append(indent + '}')

        return '\n'.join(result)


    def when(self, lst, level):
        '''Vrací obraz sekce WHEN pro Catch unit testing.'''
        result = []
        if len(lst) > 0:
            elem = lst[0]
            assert elem.type == 'when'
            identifier = elem.text.replace('"', r'\"')
            indent = ' ' * 4 * level
            result.append('{}WHEN("{}") {{'.format(indent, identifier))
            result.append(self.then(lst[1:], level + 1))
            result.append(indent + '}')

        return '\n'.join(result)


    def then(self, lst, level):
        '''Vrací obraz sekce THEN pro Catch unit testing.'''
        result = []
        if len(lst) > 0:
            elem = lst[0]
            assert elem.type == 'then'
            identifier = elem.text.replace('"', r'\"')
            indent = ' ' * 4 * level
            result.append('{}THEN("{}") {{'.format(indent, identifier))
            result.append(indent + '}')

        return '\n'.join(result)


    def parse(self):
        '''Spouštěč jednotlivých fází parseru.'''

        self.openLogFile()

        # Rozložíme .feature
        self.loadFeatureElementList()
        self.flog.write('-' * 70 + '\n')

        # ??? vytvoříme seznam identifikací scénářů a slovník podseznamů z .feature
        lst_id_feature = []
        d_feature = {}
        status = 0
        for elem in self.feature_lst:
            if status == 0:             # čekáme na 'scenario'
                if elem.type == 'scenario':
                    lst_id_feature.append(elem.text)
                    lst = [elem]
                    ##self.msg_lst.append('- ' + elem.text)
                    status = 1

            elif status == 1:           # sbíráme elementy scénáře
                if elem.type == 'empty':        # ukončení scénáře
                    k = lst[0].text           # identifikace scénáře
                    d_feature[k] = lst          # --> seznam elementů scénáře
                    status = 0
                else:
                    lst.append(elem)

        if status == 1:
            # Poslední sesbíraný scénář
            k = lst[0].text           # identifikace scénáře
            d_feature[k] = lst          # --> seznam elementů scénáře

#         # ???
#         self.msg_lst.append(('=' * 70))
#         for k in lst_id_feature:
#             lst = d_feature[k]
#             for elem in lst:
#                 self.msg_lst.append('{}, {!r}'.format(elem.type, elem.text))
#             self.msg_lst.append(('-' * 30))

        # Rozložíme .h -- pokud existuje
        self.loadTestElementList()
        self.flog.write('-' * 70 + '\n')

        # Konverze seznamu elementů pro jeden scénář do podoby .h souboru.
        with open(self.testfname, 'w', encoding='utf-8') as ftest:
            for k in lst_id_feature:
                lst = d_feature[k]
                ftest.write('\n'.join(repr(e) for e in lst))
                ftest.write('\n' + ('-' * 70) + '\n')
                ftest.write(self.scenario(lst, 0))
                ftest.write('\n' + ('=' * 70) + '\n')

        self.closeLogFile()

        return '\nParsed feature: {}\n\t'.format(self.id()) + ('\n\t'.join(self.msg_lst))
