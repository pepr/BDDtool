#!python3
"""Feature to Catch skeleton."""

import fesyn
import glob
import os
import textwrap

class CatchCodeGenerator:

    def __init__(self):
        """Default settings initialization.
        """
        self.hint_flag = True
        self.lpar = '( "'        # space after the opening parenthesis
        self.rpar = '" )'        # space before the closing parenthesis


    def append_comment(self, lst, text):
        lst.append('// ' + text)


    def append_description(self, lst, descr_list):
        lst.append('//')
        lst.extend('// ' + line for line in descr_list)


    def append_heading(self, il, lst, keyword, identifier):
        lst.append(' '*4*il + keyword + self.lpar + identifier + self.rpar + ' {')


    def append_hint(self, il, lst, text):
        if self.hint_flag:
            lst.append(' '*4*il + '// ' + text)


    def append_require(self, il, lst):
        lst.append(' '*4*il + 'REQUIRE(false);')
        lst.append('')


    def append_closing(self, il, lst):
        lst.append(' '*4*il + '}')


    def skeleton(self, syntax_tree, il):
        indent = ' ' * 4 * il
        out = []
        for item in syntax_tree:
            sym = item[0]
            if sym == 'story':
                self.append_comment(out, 'Story: ' + item[1])

            elif sym == 'feature':
                self.append_comment(out, 'Feature: ' + item[1])

            elif sym == 'description':
                self.append_description(out, item[1])

            elif sym == 'test_case':
                out.append('')
                self.append_heading(il, out, 'TEST_CASE', item[1])
                out.append('')
                out.extend(self.skeleton(item[2], il+1))
                self.append_closing(il, out)

            elif sym == 'section':
                self.append_heading(il, out, 'SECTION', item[1])
                self.append_hint(il+1, out,
                                    'perform the operation and assert the state')
                self.append_require(il+1, out)
                out.extend(self.skeleton(item[2], il+1))
                self.append_closing(il, out)

            elif sym == 'scenario':
                out.append('')
                self.append_heading(il, out, 'SCENARIO', item[1])
                out.append('')
                out.extend(self.skeleton(item[2], il+1))
                self.append_closing(il, out)

            elif sym == 'given':
                self.append_heading(il, out, 'GIVEN', item[1])
                self.append_hint(il+1, out, 'set up initial state')
                self.append_require(il+1, out)
                out.extend(self.skeleton(item[2], il+1))
                self.append_closing(il, out)

            elif sym == 'and_given':
                self.append_heading(il, out, 'GIVEN', item[1])
                self.append_hint(il+1, out, 'set up initial state')
                self.append_require(il+1, out)
                out.extend(self.skeleton(item[2], il+1))
                self.append_closing(il, out)

            elif sym == 'when':
                self.append_heading(il, out, 'WHEN', item[1])
                self.append_hint(il+1, out, 'perform operation')
                self.append_require(il+1, out)
                out.extend(self.skeleton(item[2], il+1))
                self.append_closing(il, out)

            elif sym == 'and_when':
                self.append_heading(il, out, 'AND_WHEN', item[1])
                self.append_hint(il+1, out, 'perform operation')
                self.append_require(il+1, out)
                out.extend(self.skeleton(item[2], il+1))
                self.append_closing(il, out)

            elif sym == 'then':
                self.append_heading(il, out, 'THEN', item[1])
                self.append_hint(il+1, out, 'assert expected state')
                self.append_require(il+1, out)
                out.extend(self.skeleton(item[2], il+1))
                self.append_closing(il, out)

            elif sym == 'and_then':
                self.append_heading(il, out, 'AND_THEN', item[1])
                self.append_hint(il+1, out, 'assert expected state')
                self.append_require(il+1, out)
                out.extend(self.skeleton(item[2], il+1))
                self.append_closing(il, out)

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
        cg = CatchCodeGenerator()
        lst = cg.skeleton(tree, 0)

        # Some reference to the tool.
        script_name = os.path.realpath(__file__)
        lst.append('')
        lst.append('// ----------------------------------------------------------')
        lst.append('// This skeleton was generated by ' + script_name + '.')
        lst.append('// See https://github.com/pepr/BDDtool.git')

        # Write the result to the output file.
        fout.write('\n'.join(lst))



if __name__ == '__main__':
    for fname_in in glob.glob('features/*.feature'):
        path, bname = os.path.split(fname_in)
        path2, fea = os.path.split(path)
        name, ext = os.path.splitext(bname)
        fname_out = os.path.join(path2, 'catch', name + '.catch')
        feature_to_catch_skeleton(fname_in, fname_out)