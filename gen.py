#!python3

import glob
import os
import re

featuresDir = os.path.abspath('./features')
testsDir =  os.path.abspath('./tests')

rexFeature = re.compile('^\s*(Feature|Požadavek)[^:]*:', re.IGNORECASE)
rexUserStory = re.compile('^\s*(User story)[^:]*:', re.IGNORECASE)
rexScenario = re.compile('''^\s*(Scenario|Example
                                 |Scénář|Příklad
                                 )[^:]*:\s*
                                 (?P<title>[^[]+)
                                 (?P<tags>\[.+\])\s*$''',
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

        for no, line in enumerate(fin):
            if status == 0:
                m = rexFeature.search(line)
                if m is not None:
                    fout.write('// ' + line)
                elif line.strip() == '':
                    fout.write('\n')
                    status = 1
                else:
                    flog.write('unknown {}, {}: {}'.format(no, status, line))

            elif status == 1:
                m = rexUserStory.search(line)
                if m is not None:
                    fout.write('// ' + line)
                    status = 2
                else:
                    m = rexScenario.search(line)
                    if m is not None:
                        fout.write('SCENARIO(')
                        title = m.group('title')
                        if title:
                            fout.write('"{}"'.format(title))
                        tags = m.group('tags')
                        if tags:
                            fout.write(', "{}"'.format(tags))
                        fout.write(')\n')
                        status = 4
                    else:
                        flog.write('unknown {}, {}: {}'.format(no, status, line))

            elif status == 2:   # collecting other lines of the User Story
                fout.write('// ' + line)
                if line.strip() == '':
                    status == 3
                else:
                    flog.write('unknown {}, {}: {!r}\n'.format(no, status, line))

            elif status == 3:
                m = rexScenario.search(line)
                if m is not None:
                    fout.write('SCENARIO(')
                    title = m.group('title')
                    if title:
                        fout.write('"{}"'.format(title))
                    tags = m.group('tags')
                    if tags:
                        fout.write(', "{}"'.format(tags))
                    fout.write(')\n')
                    status = 4
                else:
                    flog.write('unknown {}, {}: {}'.format(no, status, line))
