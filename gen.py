#!python3

import glob
import os
import re

def writeScenario(fout, m):
    fout.write('// {}\n'.format(m.group('label')))
    fout.write('SCENARIO(')
    title = m.group('title')
    if title:
        title = title.rstrip(). replace('"', r'\"')
        fout.write('"{}"'.format(title))
    tags = m.group('tags')
    if tags:
        fout.write(', "{}"'.format(tags))
    fout.write(') {\n')


featuresDir = os.path.abspath('./features')
testsDir =  os.path.abspath('./tests')

# Kontrola existence featuresDir a případné vytvoření testsDir.
assert os.path.isdir(featuresDir)
if not os.path.isdir(testsDir):
    os.makedirs(testsDir)

rexFeature = re.compile('^\s*(Feature|Požadavek)[^:]*:', re.IGNORECASE)
rexUserStory = re.compile('^\s*(User story)[^:]*:', re.IGNORECASE)
rexScenario = re.compile('''^\s*(?P<label>
                                  (Scenario
                                   |Example
                                   |Scénář
                                   |Příklad
                                  )
                                  (?P<extra>[^:]*):\s*
                                )
                                (?P<title>[^[]+)
                                (?P<tags>\[.+\])?\s*$''',
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
            #-----------------------------------------------------
            if status == 0:
                m = rexFeature.search(line)
                if m is not None:
                    fout.write('// ' + line)
                elif line.strip() == '':
                    fout.write('\n')
                    status = 1
                else:
                    flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            elif status == 1:
                m = rexUserStory.search(line)
                if m is not None:
                    fout.write('// ' + line)
                    status = 2
                else:
                    m = rexScenario.search(line)
                    if m is not None:
                        writeScenario(fout, m)
                        status = 4
                    else:
                        flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            elif status == 2:   # collecting other lines of the User Story
                if line.strip() != '':
                    fout.write('// ' + line)    # line of the story
                else:
                    fout.write('\n')            # separator line
                    status = 3

            #-----------------------------------------------------
            elif status == 3:
                if line.strip() == '':  # skip another separator line
                    continue

                m = rexScenario.search(line)
                if m is not None:
                    writeScenario(fout, m)
                    status = 4
                else:
                    flog.write('unknown {}, {}: {}'.format(no, status, line))

            #-----------------------------------------------------
            else:
                flog.write('unknown status {!r} {}, {}:\n{!r}\n'.format(
                              featureFname, no, status, line))
                break
