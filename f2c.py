#!python3
"""Feature to Catch skeleton."""

import fesyn
import glob
import os
import textwrap

class CatchCodeGenerator:
    """Converts a syntax tree to the Catch skeleton.

    Returns the list of text lines of the skeleton. See the skeleton() method.
    """

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
        for line in descr_list:
            if line:
                lst.append('// ' + line )
            else:
                lst.append('//')


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


    def skeleton(self, syntax_tree, il=0):
        """Returns list of lines of the skeleton from a syntax_tree.

        The il stands for the initial Indentation Level. Called recursively.
        """
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
        lst = cg.skeleton(tree)

        # Some reference to the tool.
        script_name = os.path.realpath(__file__)
        lst.append('')
        lst.append('// ----------------------------------------------------------')
        lst.append('// The skeleton was generated by ' + script_name + '.')
        lst.append('// Then the skeleton was updated manually.')
        lst.append('// See https://github.com/pepr/BDDtool.git')

        # Write the result to the output file.
        fout.write('\n'.join(lst))



if __name__ == '__main__':

    # Input directory with *.feature definitions.
    features_dir = './features'
    if not os.path.isdir(features_dir):
        os.makedirs(features_dir)

    # Output directory with generated *.h or *.skeleton files.
    tests_dir = './tests'
    if not os.path.isdir(tests_dir):
        os.makedirs(tests_dir)

    for fname_in in glob.glob(os.path.join(features_dir, '*.feature')):
        path, bname = os.path.split(fname_in)
        name, ext = os.path.splitext(bname)

        # If the header file for the skeleton does not exist, it will be
        # generated as the .h file. Otherwise, the .skeleton extension is used.
        fname_out = os.path.join(tests_dir, name + '.h')
        if os.path.isfile(fname_out):
            fname_out = os.path.join(tests_dir, name + '.skeleton')

        # Generate the skeleton.
        path, name = os.path.split(fname_in)
        path, subdir = os.path.split(path)
        src = os.path.join(subdir, name)

        path, name = os.path.split(fname_out)
        path, subdir = os.path.split(path)
        dest = os.path.join(subdir, name)

        print(src, '-->', dest)

        feature_to_catch_skeleton(fname_in, fname_out)