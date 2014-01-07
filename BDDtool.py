#!python3

import glob
import os
import sys

import feature

# Adresář s xxx.feature soubory.
features_dir = os.path.abspath('./features')

# Adresář pro xxx.h soubory s Catch testy (poprvé generované, ručně upravované
# a případně aktualizované podle .feature.
tests_dir = os.path.abspath('./tests')

# Pomocný podadresář pro logy zachycující průběh generování.
log_dir = os.path.realpath('./log')
if not os.path.isdir(log_dir):
    os.makedirs(log_dir)

# Získáme seznam všech .feature souborů a v cyklu je zpracujeme.
featureFilenames = glob.glob(os.path.join(features_dir, '*.feature'))

for featureFname in featureFilenames:
    fe = feature.Feature(featureFname, tests_dir, log_dir)
    msg = fe.parse()
    print(msg)
