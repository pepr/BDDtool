#!python3

import glob
import os
import sys

import feature

# The directory with the xxx.feature source files.
features_dir = os.path.abspath('./features')
if not os.path.isdir(testscpp_dir):
    os.makedirs(testscpp_dir)

# The directory with the xxx.h sources with Catch tests.
testscpp_dir = os.path.abspath('./testscpp')
if not os.path.isdir(testscpp_dir):
    os.makedirs(testscpp_dir)

# Auxiliary logs.
log_dir = os.path.realpath('./log')
if not os.path.isdir(log_dir):
    os.makedirs(log_dir)

# Get the list of all *.feature files and process them in the loop
# to get the *.h files for Catch.
featureFilenames = glob.glob(os.path.join(features_dir, '*.feature'))

for fname in featureFilenames:
    fe = feature.Feature(fname, testscpp_dir, log_dir)
    msg = fe.parse()
    print(msg)
