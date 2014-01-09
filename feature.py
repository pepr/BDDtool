#!python3

import elemfeature
import elemcatch
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

        self.display_lst = []    # info pro zobrazování zpracovaných souborů


    def id(self):
        '''Vrací řetězcovou identifikaci feature objektu.'''
        assert self.identifier is not None
        return self.identifier


    def openLogFile(self):
        assert self.flog is None
        self.flog = open(self.logfname, 'w', encoding='utf-8')
        self.display_lst.append('w ' + self.logfname)


    def closeLogFile(self):
        self.flog.close()
        self.flog = None


    def log(self, msg):
        self.flog.write(msg)


    def display(self, msg):
        '''Collects display lines.

        The result is used by the code that uses the object an need not
        neccessarily be displayed. The list elements should be considered
        lines without the \n. When  a multiline string is build from
        the list content, it should be joined by '\n'.'''
        self.display_lst.append(msg)


    def parseString(self, source, sourcenameinfo, elem_module):
        '''Returns the result of parsing a multiline string.

        source ........... multiline string
        sourcenameinfo ... whatever identification string
                           (e.g. bare filename), used for logs
        elem_module ...... module that implements the Element class

        Returns:
        identifier ....... the feature or story string identifier
        lst .............. list of parsed element objects
        '''

        # Split the multiline source string to get the lines, recognize
        # the elements line by line, and append them to the list.
        lst = []
        for lineno, line in enumerate(source.split('\n'), 1):
            elem = elem_module.Element(sourcenameinfo, lineno, line)
            lst.append(elem)
            self.log(repr(elem) + '\n') ##
        self.log('-' * 70 + '\n')       ##

        # Extract the Feature identifier from the 'feature' element.
        # It is recommended but not required -- initialized to empty string.
        identifier = ''
        for elem in lst:
            if elem.type == 'feature':
                identifier = elem.text
                break

        # Return the resulting feature identifier and the list of elements.
        return identifier, lst


    def parseFeatureFile(self):
        '''Returns the feature identifier and the list of elements .feature file.'''

        # Read the file content as a multiline string.
        with open(self.featurefname,  encoding='utf-8') as fin:
            source = fin.read()

        # Set the sourcenameinfo as a bare name of the input file.
        sourcenameinfo = self.feature_bare_name

        # Some info for possible output to the display.
        self.display('r ' + self.featurefname)

        # Call the parser that accepts the multiline string.
        # Pass the info including the modul that should be used
        # for the element recognition. Return the resulting tuple with
        # feature identifier and the list of elements.
        return self.parseString(source, sourcenameinfo, elemfeature)


    def loadTestElementList(self):
        '''Načte elementy z .h do členského seznamu.'''

        self.h_lst = []
        if os.path.isfile(self.testfname):
            with open(self.testfname,  encoding='utf-8') as fin:

                # Zpracujeme všechny řádky parserem.
                for lineno, line in enumerate(fin, 1):
                    elem = elemcatch.Element(self.test_bare_name, lineno, line)
                    self.feature_lst.append(elem)
                    self.log(repr(elem) + '\n')

                # Přidáme informaci o dotčených souborech.
                self.display('r ' + self.testfname)


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
        else:
            return ''


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
        else:
            return ''


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
        else:
            return ''


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
        else:
            return ''


    def parse(self):
        '''Spouštěč jednotlivých fází parseru.'''

        self.openLogFile()

        # Rozložíme .feature
        self.identifier, self.feature_lst = self.parseFeatureFile()

        # ??? vytvoříme seznam identifikací scénářů a slovník podseznamů z .feature
        lst_id_feature = []
        d_feature = {}
        status = 0
        for elem in self.feature_lst:
            if status == 0:             # čekáme na 'scenario'
                if elem.type == 'scenario':
                    lst_id_feature.append(elem.text)
                    lst = [elem]
                    ##self.display('- ' + elem.text)
                    status = 1

            elif status == 1:           # sbíráme elementy scénáře
                if elem.type == 'empty':        # ukončení scénáře
                    k = lst[0].text           # identifikace scénáře
                    d_feature[k] = lst          # --> seznam elementů scénáře
                    status = 0
                else:
                    lst.append(elem)

        if status == 1:
            # The last collected scenario.
            k = lst[0].text     # the scenario identification
            d_feature[k] = lst  # --> the list of elements of the scenario

#         # ???
#         self.display(('=' * 70))
#         for k in lst_id_feature:
#             lst = d_feature[k]
#             for elem in lst:
#                 self.display('{}, {!r}'.format(elem.type, elem.text))
#             self.display(('-' * 30))

        # Rozložíme .h -- pokud existuje
        self.loadTestElementList()
        self.log('-' * 70 + '\n')

        # Converting the list of elements to the .h file.
        output = []
        for k in lst_id_feature:
            lst = d_feature[k]
            output.append('\n'.join(repr(e) for e in lst))
            output.append('\n' + ('-' * 70) + '\n')
            output.append(self.scenario(lst, 0))
            output.append('\n' + ('=' * 70) + '\n')

        with open(self.testfname, 'w', encoding='utf-8') as ftest:
            ftest.write('\n'.join(output))

        self.closeLogFile()

        return '\nParsed feature: {}\n\t'.format(self.id()) + ('\n\t'.join(self.display_lst))
