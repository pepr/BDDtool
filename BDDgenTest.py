#!python3

import BDDgen
import os
import textwrap
import unittest

class FeatureFilePullParserTests(unittest.TestCase):

    featuresDir = os.path.abspath('./pytests/features')
    testsDir = os.path.abspath('./pytests/tests')

    def setUp(self):
        if not os.path.isdir(self.featuresDir):
            os.makedirs(self.featuresDir)

        if not os.path.isdir(self.testsDir):
            os.makedirs(self.testsDir)


    def test_open_nonexistent_feature_file(self):
         '''opening nonexistent file should raise the usuall exception'''
         fname_input = os.path.join(self.featuresDir, 'nonexistentfile.feature')
         fname_output = os.path.join(self.testsDir, 'nonexistentfile.h')
         assert not os.path.isfile(fname_input)
         assert not os.path.isfile(fname_output)

         parser = BDDgen.Parser()
         self.assertRaises(FileNotFoundError, parser.parse, fname_input)
         self.assertFalse(os.path.isfile(fname_output))
         
         
    def test_empty_input_empty_output(self):
         '''existing but empty.feature file should generate the empty.h'''
         fname_input = os.path.join(self.featuresDir, 'empty.feature')
         fname_output = os.path.join(self.testsDir, 'empty.h')
 
         # Remove the older files.
         if os.path.isfile(fname_input): 
             os.remove(fname_input)
         if os.path.isfile(fname_output): 
             os.remove(fname_output)
         
         with open(fname_input, 'w') as f:
             pass
         self.assertTrue(os.path.isfile(fname_input))

         parser = BDDgen.Parser()
         with open(fname_output, 'w') as fout:
             fout.write(''.join(parser.parse(fname_input)))
                  
         self.assertTrue(os.path.isfile(fname_output))
         self.assertEqual(os.path.getsize(fname_output), 0)
         


if __name__ == '__main__':
    unittest.main()