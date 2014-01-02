#!python3

import glob
import os
import re


class CodeBlock:

    def __init__(self, fout, indent_level=0, prev=None):
        self.fout = fout
        self.flog = flog
        self.indent_level = indent_level
        self.prev = prev

    def out(self, txt, indent=True):
        if indent:
            self.fout.write('    ' * self.indent_level)
        self.fout.write(txt)

    def push(self):
        block = CodeBlock(self.fout, self.indent_level, self)
        return block
    
    def indent(self):
        self.indent_level += 1

    def dedent(self):
        self.indent_level -= 1


    def writeScenario(self, m):
        self.out('// {}\n'.format(m.group('label')))
        self.out('SCENARIO(')
        title = m.group('title')
        if title:
            title = title.rstrip(). replace('"', r'\"')
            self.out('"{}"'.format(title), False)
        tags = m.group('tags')
        if tags:
            self.out(', "{}"'.format(tags), False)
        self.out(') {\n', False)


    def writeTextForSection(self, sec, m, indent=True):
        self.out(sec + '(', False)
        text = m.group('text')
        if text:
            text = text.rstrip().replace('"', r'\"')
            self.out('"{}"'.format(text), False)
        self.out(') {\n', False)


featuresDir = os.path.abspath('./features')
testsDir =  os.path.abspath('./tests')

# Kontrola existence featuresDir a případné vytvoření testsDir.
assert os.path.isdir(featuresDir)
if not os.path.isdir(testsDir):
    os.makedirs(testsDir)

rexFeature = re.compile('^\s*(Feature|Požadavek)[^:]*:', re.IGNORECASE)
rexUserStory = re.compile('^\s*(User story)[^:]*:', re.IGNORECASE)
rexScenario = re.compile('''^\s*(?P<label>(Scenario|Example
                                           |Scénář|Příklad)
                                  (?P<extra>[^:]*):\s*
                                )
                                (?P<title>[^[]+)
                                (?P<tags>\[.+\])?\s*$''',
                         re.IGNORECASE | re.VERBOSE)
rexGiven = re.compile('''^\s*(Given|Dáno)\s*:\s*
                             (?P<text>.+)\s*$''',
                         re.IGNORECASE | re.VERBOSE)
rexWhen = re.compile('''^\s*(When|Když)\s*:\s*
                            (?P<text>.+)\s*$''',
                         re.IGNORECASE | re.VERBOSE)
rexThen = re.compile('''^\s*(Then|Pak)\s*:\s*
                            (?P<text>.+)\s*$''',
                         re.IGNORECASE | re.VERBOSE)

featureFilenames = glob.glob(os.path.join(featuresDir, '*.feature'))

for featureFname in featureFilenames:
    basename = os.path.basename(featureFname)
    name, ext = os.path.splitext(basename)
    testFname = os.path.join(testsDir, name + '.h')
    print(basename, '-->', testFname)

    with open(featureFname, encoding='utf8') as fin, \
         open(testFname, 'w', encoding='utf8') as fout, \
         open(featureFname + '.log', 'w', encoding='utf8') as flog:

        status = 0

        code = CodeBlock(fout)

        for no, line in enumerate(fin):
            #-----------------------------------------------------
            if status == 0:
                m = rexFeature.search(line)
                if m is not None:
                    code.out('// ' + line)
                elif line.strip() == '':
                    code.out('\n')
                    status = 1
                else:
                    m = rexScenario.search(line)
                    if m is not None:
                        code.writeScenario(m)
                        status = 4
                    else:
                        flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            elif status == 1:
                m = rexUserStory.search(line)
                if m is not None:
                    code.out('// ' + line)
                    status = 2
                else:
                    m = rexScenario.search(line)
                    if m is not None:
                        code.writeScenario(m)
                        status = 4
                    else:
                        flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            elif status == 2:   # collecting other lines of the User Story
                if line.strip() != '':
                    code.out('// ' + line)      # line of the story
                else:
                    code.out('\n', False)       # separator line
                    status = 3

            #-----------------------------------------------------
            elif status == 3:   # waiting for "Scenario: ..."
                m = rexScenario.search(line)
                if m is not None:
                    code.writeScenario(m)
                    status = 4
                elif line.strip() == '':
                    pass # skip another separator line
                else:
                    flog.write('unknown {}, {}: {!r}\n'.format(no, status, line))

            #-----------------------------------------------------
            elif status == 4:
                m = rexGiven.search(line)
                if m is not None:
                    code.indent()
                    code.writeTextForSection('GIVEN', m)
                    status = 5
                else:
                    flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            elif status == 5:
                if line.strip() == '':  # earlier finished scenario - sep. line
                    code.dedent()
                    code.out('}\n\n', False)    # scenario finished
                    status = 3
                else:
                    m = rexWhen.search(line)
                    if m is not None:
                        code.indent()
                        code.writeTextForSection('WHEN', m)
                        status = 6
                    else:
                        flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            elif status == 6:
                m = rexThen.search(line)
                if m is not None:
                    code.indent()
                    code.writeTextForSection('THEN', m)
                    status = 7
                elif line.strip() == '':  # earlier finished "given" - sep. line
                    code.dedent()
                    code.out('}\n')       # of Given
                    code.dedent()
                    code.out('}\n')       # of Scenario
                    status = 3
                else:
                    flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            elif status == 7:
                if line.strip() == '':  # separator line
                    code.dedent()
                    code.out('}\n')    # of Then
                    code.dedent()
                    code.out('}\n')    # of When
                    code.dedent()
                    code.out('}\n')    # of Scenario
                    status = 3
                else:
                    flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            else:
                flog.write('unknown status {!r} {}, {}:\n{!r}\n'.format(
                              featureFname, no, status, line))
                break
