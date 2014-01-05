#!python3

import docelement
import os

class Parser:
    '''Parser pro rozklad xxx.feature a odpovídajícího xxx.h.'''

    def __init__(self, fname, log_dir):
        self.fname = fname      # jméno .feature souboru
        self.log_dir = log_dir  # adresář pro log soubory

        self.feature_lst = None # seznam elementů z .feature
        self.h_lst = None       # seznam elementů z .h

        self.info_files = []    # info pro zobrazování zpracovaných souborů


    def loadFeatureElementList(self):
        '''Načte elementy z .feature do členského seznamu.'''

        basename = os.path.basename(self.fname)
        logname = os.path.join(self.log_dir, basename  + '.log')
        self.feature_lst = []
        with open(self.fname,  encoding='utf-8') as fin,\
             open(logname, 'w', encoding='utf-8') as flog:
            
            # Zpracujeme všechny řádky parserem.
            for lineno, line in enumerate(fin, 1):
                elem = docelement.Element(basename, lineno, line)
                self.feature_lst.append(elem)
                flog.write(repr(elem) + '\n')

            # Přidáme informaci o dotčených souborech.
            self.info_files.append(self.fname)
            self.info_files.append(logname)
            

    def run(self):
        '''Spouštěč jednotlivých fází parseru.'''

        self.loadFeatureElementList()

        return '\n\t'.join(self.info_files)
