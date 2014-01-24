#!python3
# -*- coding: utf-8 -*-
import os
import textwrap
import unittest

import sys
sys.path.append('..')

import tsyn

class SyntaxCatchTests(unittest.TestCase):
    '''Testing syntax analysis for the Catch test sources.'''


    def test_empty(self):
        '''empty Catch test source'''

        source = ''


    def test_story(self):

        source = '// Story: story identifier'
        sa = tsyn.SyntacticAnalyzerForCatch(source)
        sa.lex()                # prepare the first lexical token
        lst = list(sa.Start())  # run from the start nonterminal
        self.assertEqual(len(lst), 1)
        self.assertEqual(lst, [('story', 'story identifier')])


        source = textwrap.dedent('''\
            // Story: story identifier
            //
            //  As a user
            //  I want the feature
            //  so that my life is to be easier.

            ''')

        sa = tsyn.SyntacticAnalyzerForCatch(source)
        sa.lex()                # prepare the first lexical token
        lst = list(sa.Start())  # run from the start nonterminal
        self.assertEqual(len(lst), 2)
        self.assertEqual(lst, [
            ('story', 'story identifier'),
            ('storybody', 'As a user\nI want the feature\nso that my life is to be easier.')
        ])


    def test_complex_source(self):
        source = textwrap.dedent('''\
            // Story: story identifier
            //
            //  As a user
            //  I want the feature
            //  so that my life is to be easier.

            SCENARIO( "scenario identifier" ) {
                GIVEN( "given identifier" ) {
                    // set up initial state

                    WHEN( "when identifier" ) {
                        // perform operation

                        THEN( "then identifier" ) {
                            // assert expected state
                        }
                    }
                }
            }
            ''')

        sa = tsyn.SyntacticAnalyzerForCatch(source)
        sa.lex()            # prepare the first lexical token
        sa.Start()          # run from the start nonterminal


if __name__ == '__main__':
    unittest.main()