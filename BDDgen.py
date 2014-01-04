#!python3

import os

START_DOCUMENT = 'START_DOCUMENT'
END_DOCUMENT = 'END_DOCUMENT'

SEPARATOR_LINE = 'SEPARATOR_LINE'

START_FEATURE = 'START_FEATURE'
END_FEATURE = 'END_FEATURE'

START_SCENARIO = 'START_SCENARIO'
END_SCENARIO = 'END_SCENARIO'

START_GIVEN = 'START_GIVEN'
END_GIVEN = 'END_GIVEN'

START_WHEN = 'START_WHEN'
END_WHEN = 'END_WHEN'

START_THEN = 'START_THEN'
END_THEN = 'END_THEN'

class Parser:
    
    def parse(self, fname, encoding='utf_8'):
        self.fin = open(fname, encoding=encoding)
        yield ''
        self.fin.close()

