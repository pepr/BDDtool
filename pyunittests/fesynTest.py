#!python3
import os
import textwrap
import unittest

import sys
sys.path.append('..')

import fesyn

class SyntaxFeatureTests(unittest.TestCase):
    """Testing syntax analysis for the .feature test sources.
    """

    def test_empty(self):
        """empty .feature test source"""

        source = ''
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(tree, [])


    def test_title_only(self):
        """The feature or story title only, no section or scenario def.
        """
        source = 'Feature: feature title'
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [('feature', 'feature title')])

        source = 'Story: story title'
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [('story', 'story title')])


    def test_story_with_description(self):
        """The feature or story with a title and a description.
        """
        source = textwrap.dedent('''\
            Feature: feature title

            The feature description is just some text.

            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 2)
        self.assertEqual(tree, [
            ('feature', 'feature title'),
            ('description', [
                'The feature description is just some text.',
                '',
                ''
            ])
        ])


        source = textwrap.dedent('''\
            Story: story title

            As a user
            I want the feature
            so that my life is to be easier.

            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 2)
        self.assertEqual(tree, [
            ('story', 'story title'),
            ('description', [
                 'As a user',
                 'I want the feature',
                 'so that my life is to be easier.',
                 '',
                 ''
             ])
        ])


    def test_scenario_only(self):
        """Scenario only
        """
        source = 'Scenario: scenario identifier'
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [])
        ])

        source = textwrap.dedent('''\
            Scenario: scenario identifier 1

            Scenario: scenario identifier 2
            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 2)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier 1', []),
            ('scenario', 'scenario identifier 2', [])
        ])


    def test_scenario_given(self):
        """Scenario, given, but no when and then
        """
        source = textwrap.dedent('''\
            Scenario: scenario identifier
               Given: given identifier
            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                ])
            ])
        ])


    def test_scenario_given_when_no_then(self):
        """Scenario, given, when, but no then
        """
        source = textwrap.dedent('''\
            Scenario: scenario identifier
               Given: given identifier
                When: when identifier''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                    ('when', 'when identifier', [])
                ])
            ])
        ])


    def test_scenario_given_when_then(self):
        """Scenario, given, when, then
        """
        source = textwrap.dedent('''\
            Scenario: scenario identifier
               Given: given identifier
                When: when identifier
                Then: then identifier''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                    ('when', 'when identifier', [
                        ('then', 'then identifier', [
                        ])
                    ])
                ])
            ])
        ])


    def test_two_scenarios(self):
        """Scenario, given, when, then and another one of the same structure
        """
        source = textwrap.dedent('''\
            Scenario: scenario identifier
               Given: given identifier
                When: when identifier
                Then: then identifier

            Scenario: scenario identifier
               Given: given identifier
                When: when identifier
                Then: then identifier

            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 2)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                    ('when', 'when identifier', [
                        ('then', 'then identifier', [
                        ])
                    ])
                ])
            ]),
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                    ('when', 'when identifier', [
                        ('then', 'then identifier', [
                        ])
                    ])
                ])
            ]),
        ])


    def test_case_only(self):
        """test case only
        """
        source = textwrap.dedent('Test: test identifier')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('test_case', 'test identifier', [])
        ])


    def test_story_scenario_given_when_then_strict_format(self):
        """Scenario, given, when, then -- strict format.
        """
        source = textwrap.dedent('''\
            Story: story identifier

            As a user
            I want the feature
            so that my life is to be easier.

            Scenario: scenario identifier
               Given: given identifier
                When: when identifier
                Then: then identifier
            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 3)
        self.assertEqual(tree, [
            ('story', 'story identifier'),
            ('description', [
                 'As a user',
                 'I want the feature',
                 'so that my life is to be easier.',
                 ''
            ]),
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                    ('when', 'when identifier', [
                        ('then', 'then identifier', [
                        ])
                    ])
                ])
            ])
        ])


    def test_scenario_with_more_givens(self):
        """Scenario with more given's
        """
        source = textwrap.dedent('''\
            Scenario: scenario identifier

               Given: given identifier
                When: when identifier
                Then: then identifier

               Given: given identifier 2
                When: when identifier 2
                Then: then identifier 2
            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                    ('when', 'when identifier', [
                        ('then', 'then identifier', [
                        ])
                    ])
                ]),
                ('given', 'given identifier 2', [
                    ('when', 'when identifier 2', [
                        ('then', 'then identifier 2', [
                        ])
                    ])
                ])
            ])
        ])

        # More of given's with empty definitions must be accepted.
        source = textwrap.dedent('''\
            Scenario: scenario identifier

               Given: given identifier

               Given: given identifier 2

            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', []),
                ('given', 'given identifier 2', []),
            ])
        ])



    def test_scenario_given_and_given(self):
        """Scenario, given, and_given
        """
        source = textwrap.dedent('''\
            Scenario: scenario identifier
               Given: given identifier
                 and: given 2 identifier
            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                    ('and_given', 'given 2 identifier', [
                    ])
                ])
            ])
        ])


    def test_scenario_given_but(self):
        """Scenario, given, but transformed to and_given
        """
        source = textwrap.dedent('''\
            Scenario: scenario identifier
               Given: given identifier
                 but: but identifier
            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                    ('and_given', 'but identifier', [
                    ])
                ])
            ])
        ])


    def test_scenario_when_but(self):
        """Scenario, given, when, but transformed to and_when
        """
        source = textwrap.dedent('''\
            Scenario: scenario identifier
               Given: given identifier
                When: when identifier
                 but: but identifier
            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                    ('when', 'when identifier', [
                        ('and_when', 'but identifier', [
                        ])
                    ])
                ])
            ])
        ])


    def test_scenario_given_more_whens(self):
        """Scenario, given, and more when's
        """
        source = textwrap.dedent('''\
            Scenario: scenario identifier
               Given: given identifier
                When: when identifier
                Then: then identifier
                 and: and_then identifier
                When: when identifier 2
                Then: then identifier 2
            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                    ('when', 'when identifier', [
                        ('then', 'then identifier', [
                            ('and_then', 'and_then identifier', [
                            ])
                        ])
                    ]),
                    ('when', 'when identifier 2', [
                        ('then', 'then identifier 2', [
                        ])
                    ])
                ])
            ])
        ])


    def test_scenario_more_then_error(self):
        """Scenario a sequence of more then's must fail
        """
        source = textwrap.dedent('''\
            Scenario: scenario identifier
               Given: given identifier
                When: when identifier
                Then: then identifier
                Then: then identifier 2
            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        self.assertRaises(RuntimeError, sa.Start)


    def test_scenario_andX(self):
        """Scenario with and's everywhere
        """
        source = textwrap.dedent('''\
            Scenario: scenario identifier
               Given: given identifier
                 and: given 2 identifier
                When: when identifier
                 and: when 2 identifier
                Then: then identifier
                 and: then 2 identifier
            ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'scenario identifier', [
                ('given', 'given identifier', [
                    ('and_given', 'given 2 identifier', [
                        ('when', 'when identifier', [
                            ('and_when', 'when 2 identifier', [
                                ('then', 'then identifier', [
                                    ('and_then', 'then 2 identifier', [
                                    ])
                                ])
                            ])
                        ])
                    ])
                ])
            ])
        ])


    def test_Czech_complex_story(self):
        """Czech complex story
        """
        source = textwrap.dedent('''\
            Požadavek: vytvoření plánu z výsledku analýzy

            Jako běžný uživatel
            chci vytvořit plán z výsledku analýzy,
            protože ruční vytváření plánu je pracné.

            Rozbor: Plán má podobu datové kostky.


            Scénář: schopnost zjistit existující kostku plánu pro danou analýzu
              Dáno: vlastnosti (typ, atributy) analýzy
              Když: vyhodnotíme atributy analýzy
                 a: kostka plánu existuje
               Pak: jsme schopni vrátit atributy existující kostky plánu


            Scénář: schopnost zjistit neexistenci kostky plánu
              Dáno: vlastnosti (typ, atributy) analýzy
              Když: vyhodnotíme atributy analýzy
                 a: kostka plánu neexistuje
               Pak: jsme schopni vrátit atributy budoucí kostky plánu
        ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 4)
        self.assertEqual(tree, [
            ('story', 'vytvoření plánu z výsledku analýzy'),
            ('description', [
                'Jako běžný uživatel',
                'chci vytvořit plán z výsledku analýzy,',
                'protože ruční vytváření plánu je pracné.',
                '',
                'Rozbor: Plán má podobu datové kostky.',
                '',
                ''
            ]),
            ('scenario', 'schopnost zjistit existující kostku plánu pro danou analýzu', [
                ('given', 'vlastnosti (typ, atributy) analýzy', [
                    ('when', 'vyhodnotíme atributy analýzy', [
                        ('and_when', 'kostka plánu existuje', [
                            ('then', 'jsme schopni vrátit atributy existující kostky plánu', [
                            ])
                        ])
                    ])
                ])
            ]),
            ('scenario', 'schopnost zjistit neexistenci kostky plánu', [
                ('given', 'vlastnosti (typ, atributy) analýzy', [
                    ('when', 'vyhodnotíme atributy analýzy', [
                        ('and_when', 'kostka plánu neexistuje', [
                            ('then', 'jsme schopni vrátit atributy budoucí kostky plánu', [
                            ])
                        ])
                    ])
                ])\
            ])
        ])

        #---------------------------------------------------------------------
        source = textwrap.dedent('''\
          Scénář: rozhodnutí o nutnosti přenosu přílohy
            Je dána příloha...
            Když se časy příloh liší,
            ale kontrolní součet se shoduje,
            pak se přesun neplánuje
            a čas se upraví.
        ''')
        sa = fesyn.SyntacticAnalyzerForFeature(source)
        tree = sa.Start()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree, [
            ('scenario', 'rozhodnutí o nutnosti přenosu přílohy', [
                ('given', 'příloha...', [
                    ('when', 'se časy příloh liší,', [
                        ('and_when', 'kontrolní součet se shoduje,', [
                            ('then', 'se přesun neplánuje', [
                                ('and_then', 'čas se upraví.', [
                                ])
                            ])
                        ])
                    ])
                ])
            ]),
        ])


if __name__ == '__main__':
    unittest.main()