#!python3

import glob
import os
import re


class CodeBlock:

    def __init__(self, fout, indent_level=0, identifier='TOP', prev=None):
        self.identifier = identifier
        self.fout = fout
        self.indent_level = indent_level
        self.prev = prev


    def out(self, txt, indent=False):
        if indent:
            self.fout.write('    ' * self.indent_level)
        self.fout.write(txt)


    def push(self, identifier, m):
        block = CodeBlock(self.fout, self.indent_level, identifier, self)
        assert m is not None    # match object with groups
        if identifier == 'SCENARIO':
            block.writeScenarioHead(m)
            block.indent()
        elif identifier in ('GIVEN', 'WHEN', 'THEN'):
            block.writeHeadForSection(identifier, m)
            block.indent()
        else:
            assert False
        return block


    def closePop(self, identifier=None):
        assert (identifier is None) or (self.identifier == identifier)
        self.dedent()
        self.out('}\n', True)
        prev = self.prev
        return prev


    def indent(self):
        self.indent_level += 1


    def dedent(self):
        self.indent_level -= 1


    def writeScenarioHead(self, m):
        self.out('// {}\n'.format(m.group('label')), True)
        self.out('SCENARIO(', True)
        title = m.group('title')
        if title:
            title = title.rstrip(). replace('"', r'\"')
            self.out('"{}"'.format(title))
        tags = m.group('tags')
        if tags:
            self.out(', "{}"'.format(tags))
        self.out(') {\n')


    def writeHeadForSection(self, sec, m, indent=True):
        self.out(sec + '(', True)
        text = m.group('text')
        if text:
            text = text.rstrip().replace('"', r'\"')
            self.out('"{}"'.format(text))
        self.out(') {\n')


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

        block = CodeBlock(fout)

        for no, line in enumerate(fin):
            #-----------------------------------------------------
            if status == 0:
                m = rexFeature.search(line)
                if m is not None:
                    block.out('// ' + line)
                elif line.strip() == '':
                    block.out('\n')
                    status = 1
                else:
                    m = rexScenario.search(line)
                    if m is not None:
                        block = block.push('SCENARIO', m)
                        status = 4
                    else:
                        flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            elif status == 1:
                m = rexUserStory.search(line)
                if m is not None:
                    block.out('// ' + line)
                    status = 2
                else:
                    m = rexScenario.search(line)
                    if m is not None:
                        block = block.push('SCENARIO', m)
                        status = 4
                    else:
                        flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            elif status == 2:   # collecting other lines of the User Story
                if line.strip() != '':
                    block.out('// ' + line)      # line of the story
                else:
                    block.out('\n', False)       # separator line
                    status = 3

            #-----------------------------------------------------
            elif status == 3:   # waiting for "Scenario: ..."
                m = rexScenario.search(line)
                if m is not None:
                    block = block.push('SCENARIO', m)
                    status = 4
                elif line.strip() == '':
                    pass # skip another separator line
                else:
                    flog.write('unknown {}, {}: {!r}\n'.format(no, status, line))

            #-----------------------------------------------------
            elif status == 4:
                m = rexGiven.search(line)
                if m is not None:
                    assert block.identifier == 'SCENARIO'
                    block = block.push('GIVEN', m)
                    status = 5
                else:
                    flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            elif status == 5:
                if line.strip() == '':  # earlier finished scenario - sep. line
                    block = block.closePop('GIVEN')
                    block = block.closePop('SCENARIO')
                    assert block.identifier == 'TOP'
                    status = 3
                else:
                    m = rexWhen.search(line)
                    if m is not None:
                        assert block.identifier == 'GIVEN'
                        block = block.push('WHEN', m)
                        status = 6
                    else:
                        flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            elif status == 6:
                m = rexThen.search(line)
                if m is not None:
                    assert block.identifier == 'WHEN'
                    block = block.push('THEN', m)
                    status = 7
                elif line.strip() == '':  # earlier finished "given" - sep. line
                    block = block.closePop('WHEN')
                    block = block.closePop('GIVEN')
                    block = block.closePop('SCENARIO')
                    if block.identifier != 'TOP':
                        flog.write('TOP block expected {}, {}, {}: {}'.format(
                                    no, status, block.identifier, line))
                    status = 3
                else:
                    flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            elif status == 7:
                if line.strip() == '':  # separator line
                    block = block.closePop('THEN')
                    block = block.closePop('WHEN')
                    block = block.closePop('GIVEN')
                    block = block.closePop('SCENARIO')
                    block.identifier == 'TOP'
                    status = 3
                else:
                    flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            else:
                flog.write('unknown status {!r} {}, {}:\n{!r}\n'.format(
                              featureFname, no, status, line))
                break
