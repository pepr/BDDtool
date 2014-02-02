#!python3
import os
import textwrap
import unittest

import sys
sys.path.append('..')

import tsyn

class SyntaxCatchTests(unittest.TestCase):
    """Testing syntax analysis for the Catch test sources."""


    def test_empty(self):
        """empty Catch test source"""

        source = ''
        sa = tsyn.SyntacticAnalyzerForCatch(source)
        tree = sa.Start()       # build the syntaxt tree from the start nonterminal
        self.assertEqual(len(tree), 0)


    def test_story(self):

        source = '// Story: story identifier'
        sa = tsyn.SyntacticAnalyzerForCatch(source)
        tree = sa.Start()       # build the syntaxt tree from the start nonterminal
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [('story', 'story identifier')])


        source = textwrap.dedent('''\
            // Story: story identifier
            //
            //  As a user
            //  I want the feature
            //  so that my life is to be easier.

            ''')

        sa = tsyn.SyntacticAnalyzerForCatch(source)
        tree = sa.Start()       # build the syntaxt tree from the start nonterminal
        self.assertEqual(len(tree), 2)
        self.assertEqual(tree, [
            ('story', 'story identifier'),
            ('description',
             '\n  As a user\n  I want the feature\n  so that my life is to be easier.')
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
                }
            }
            ''')
        sa = tsyn.SyntacticAnalyzerForCatch(source)
        tree = sa.Start()       # build the syntaxt tree from the start nonterminal
        self.assertEqual(len(tree), 3)

        self.assertEqual(tree, [
            ('story', 'story identifier'),
            ('description',
             '\n  As a user\n  I want the feature\n  so that my life is to be easier.'),
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                ])
            ])
        ])


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
        tree = sa.Start()       # build the syntaxt tree from the start nonterminal
        self.assertEqual(len(tree), 3)

        self.assertEqual(tree, [
            ('story', 'story identifier'),
            ('description',
             '\n  As a user\n  I want the feature\n  so that my life is to be easier.'),
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                    ('when', 'when identifier', [
                        ('then', 'then identifier', [
                        ])
                    ])
                ])
            ])
        ])



if __name__ == '__main__':
    unittest.main()