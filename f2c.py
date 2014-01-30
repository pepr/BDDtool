#!python3
'''Feature to Catch skeleton.'''

import fesyn
import textwrap

def skeleton(syntax_tree, il):
    indent = ' ' * 4 * il
    out = []
    for item in syntax_tree:
        sym = item[0]
        if sym == 'story':
            out.append('// Story: ' + item[1])

        elif sym == 'description':
            lst = item[1].split('\n')
            out.extend('// ' + line for line in lst)

        elif sym == 'scenario':
            out.append(indent + 'SCENARIO( "' + item[1] + '" ) {')
            out.extend(skeleton(item[2], il+1))
            out.append(indent + '}')

        elif sym == 'given':
            out.append(indent + 'GIVEN( "' + item[1] + '" ) {')
            out.append(indent + '    // set up initial state')
            out.append('')
            out.extend(skeleton(item[2], il+1))
            out.append(indent + '}')

        elif sym == 'when':
            out.append(indent + 'WHEN( "' + item[1] + '" ) {')
            out.append(indent + '    // perform operation')
            out.append('')
            out.extend(skeleton(item[2], il+1))
            out.append(indent + '}')

        elif sym == 'then':
            out.append(indent + 'THEN( "' + item[1] + '" ) {')
            out.append(indent + '    // assert expected state')
            out.append('')
            out.extend(skeleton(item[2], il+1))
            out.append(indent + '}')

        else:
            raise NotImplementedError('Symbol: ' + sym)
    return out


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

    lst = skeleton(tree, 0)
    print('\n'.join(lst))