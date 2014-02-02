#!python3
"""Feature to Catch skeleton."""

import fesyn
import glob
import os
import textwrap


def skeleton(syntax_tree, il):
    indent = ' ' * 4 * il
    out = []
    for item in syntax_tree:
        sym = item[0]
        if sym == 'story':
            out.append('// Story: ' + item[1])

        elif sym == 'description':
            out.append('//')
            lst = item[1].split('\n')
            out.extend('// ' + line for line in lst)

        elif sym == 'scenario':
            out.append('')
            out.append(indent + 'SCENARIO("' + item[1] + '") {')
            out.append('')
            out.extend(skeleton(item[2], il+1))
            out.append(indent + '}')

        elif sym == 'given':
            out.append(indent + 'GIVEN("' + item[1] + '") {')
            out.append(indent + '    // set up initial state')
            out.append(indent + '    REQUIRE(false);')
            out.append('')
            out.extend(skeleton(item[2], il+1))
            out.append(indent + '}')

        elif sym == 'and_given':
            out.append(indent + 'GIVEN("' + item[1] + '") {')
            out.append(indent + '    // set up initial state')
            out.append(indent + '    REQUIRE(false);')
            out.append('')
            out.extend(skeleton(item[2], il+1))
            out.append(indent + '}')

        elif sym == 'when':
            out.append(indent + 'WHEN("' + item[1] + '") {')
            out.append(indent + '    // perform operation')
            out.append(indent + '    REQUIRE(false);')
            out.append('')
            out.extend(skeleton(item[2], il+1))
            out.append(indent + '}')

        elif sym == 'and_when':
            out.append(indent + 'AND_WHEN("' + item[1] + '") {')
            out.append(indent + '    // perform operation')
            out.append(indent + '    REQUIRE(false);')
            out.append('')
            out.extend(skeleton(item[2], il+1))
            out.append(indent + '}')

        elif sym == 'then':
            out.append(indent + 'THEN("' + item[1] + '") {')
            out.append(indent + '    // assert expected state')
            out.append(indent + '    REQUIRE(false);')
            out.append('')
            out.extend(skeleton(item[2], il+1))
            out.append(indent + '}')

        elif sym == 'and_then':
            out.append(indent + 'AND_THEN("' + item[1] + '") {')
            out.append(indent + '    // assert expected state')
            out.append(indent + '    REQUIRE(false);')
            out.append('')
            out.extend(skeleton(item[2], il+1))
            out.append(indent + '}')

        else:
            raise NotImplementedError('Symbol: ' + sym)
    return out


def feature_to_catch_skeleton(fname_in, fname_out):
    """Converts the source of the feature structure to the Catch source skeleton.
    """
    # Open the input file with the feature description and the output file
    # for the Catch source skeleton.
    with open(fname_in, encoding='utf_8') as fin, \
         open(fname_out, 'w', encoding='utf_8') as fout:

        # Get the syntax tree for the feature description.
        sa = fesyn.SyntacticAnalyzerForFeature(fin)
        tree = sa.Start()
        ##print(tree)

        # Generate the lines of the skeleton from the syntaxt tree.
        lst = skeleton(tree, 0)

        # Some reference to the tool.
        script_name = os.path.realpath(__file__)
        lst.append('')
        lst.append('// ----------------------------------------------------------')
        lst.append('// This skeleton was generated by ' + script_name + '.')
        lst.append('// See https://github.com/pepr/BDDtool.git')

        # Write the result to the output file.
        fout.write('\n'.join(lst))



if __name__ == '__main__':
    feature_to_catch_skeleton('planZAnalyzy.feature', 'planZAnalyzy.catch')