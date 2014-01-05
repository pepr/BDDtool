#!python3

import glob
import os
import sys

import featureparser

# Adresář s originálními podadresáři a soubory.
features_dir = os.path.abspath('./features')

# Pomocný podadresář pro logy zachycující průběh generování.
log_dir = os.path.realpath('./log')
if not os.path.isdir(log_dir):
    os.makedirs(log_dir)

# Získáme seznam všech .feature souborů a v cyklu je zpracujeme.
featureFilenames = glob.glob(os.path.join(features_dir, '*.feature'))

for featureFname in featureFilenames:
    print('Parsing:')
    parser = featureparser.Parser(featureFname, log_dir)
    msg = parser.run()
    print('\t' + msg)
