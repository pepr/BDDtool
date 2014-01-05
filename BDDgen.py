#!python3

import glob
import os
import sys

import elemparser

# Adresář s originálními podadresáři a soubory.
features_dir = os.path.abspath('./features')

# Pomocný podadresář pro generované informace.
aux_dir = os.path.realpath('./aux_dir')
if not os.path.isdir(aux_dir):
    os.makedirs(aux_dir)

featureFilenames = glob.glob(os.path.join(features_dir, '*.feature'))

for featureFname in featureFilenames:
    print('Parsing:')
    pa = elemparser.Parser(featureFname, 'a.h', aux_dir)
    msg = pa.run()
    print('\t' + msg)
