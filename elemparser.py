#!python3

import docelement
import os

class Parser:
    '''Parser pro rozklad .feature a odpovídajícího .h.'''

    def __init__(self, features_name, h_name, aux_dir):
        self.features_name = features_name   # jméno .feature souboru
        self.h_name = h_name            # jméno odpovídajícího .h souboru
        self.aux_dir = aux_dir          # pomocný adresář

        self.feature_lst = None         # seznam elementů z .feature
        self.h_lst = None               # seznam elementů z .h

        self.info_files = []


    def loadElementLists(self):
        '''Načte elementy z .feature a .h do členských seznamů.

           Jako vedlejší efekt zachytí reprezentaci seznamů elementů
           do souborů passFeature.txt a passH.txt v pomocném adresáři.'''

        # Elementy z xxx.feature.
        self.feature_lst = []
        with open(self.features_name,  encoding='utf-8') as fin,\
             open(os.path.join(self.aux_dir, 'passFeature.txt'), 'a',
                  encoding='utf-8') as fout:
            fout.write('-' * 70 + '\n')
            self.info_files.append(self.features_name)
            relname = os.path.basename(self.features_name) # holé jméno do logu
            for lineno, line in enumerate(fin, 1):
                elem = docelement.Element(relname, lineno, line)
                self.feature_lst.append(elem)
                fout.write(repr(elem) + '\n')

        # Přidáme informaci o výstupním souboru.
        subdir = os.path.basename(self.aux_dir)
        self.info_files.append(subdir +'/passFeature.txt')

        # Elementy z xxx.h.
        self.en_lst = []
        if os.path.isfile(self.h_name):
            with open(self.h_name,  encoding='utf-8') as fin,\
                 open(os.path.join(self.aux_dir, 'passH.txt'), 'a',
                      encoding='utf-8') as fout:
                fout.write('-' * 70 + '\n')
                self.info_files.append(self.features_name)
                relname = os.path.basename(self.h_name) # holé jméno do logu
                for lineno, line in enumerate(fin, 1):
                    elem = docelement.Element(relname, lineno, line)
                    self.h_lst.append(elem)
                    fout.write(repr(elem) + '\n')

            # Přidáme informaci o výstupním souboru.
            subdir = os.path.basename(self.aux_dir)
            self.info_files.append(subdir +'/passH.txt')


    def run(self):
        '''Spouštěč jednotlivých fází parseru.'''

        self.loadElementLists()

        return '\n\t'.join(self.info_files)
