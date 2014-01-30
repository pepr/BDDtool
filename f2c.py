#!python3
'''Feature to Catch skeleton.'''

import fesyn
import textwrap

def catchSkeleton(syntax_tree):

    for item in syntax_tree:
        sym = item[0]
        if sym == 'story':
            yield '// Story: ' + item[1] + '\n'
        
        elif sym == 'description':
            lst = item[1].split('\n')
            out_lst = ['// ' + line for line in lst]
            yield '\n'.join(out_lst) + '\n'
        
        elif sym == 'scenario':
            assert len(item) == 3
            scenarioSkeleton(item[1], item[2])  # identifier, body item list
        else:    
            raise ErrorNotImplemented('Symbol: ' + sym)


def scenarioSkeleton(identifier, body_lst):
    yield 'SCENARIO( "' + identifier + '" ) {\n'
    for item in bodylst:
        sym = item[0]
        raise ErrorNotImplemented('Symbol: ' + sym)
        
          

if __name__ == '__main__':
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

    for line in catchSkeleton(tree):
        print(line, end='')