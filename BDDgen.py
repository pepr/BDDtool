#!python3

import os

class Parser:
    
    def parse(self, fname, encoding='utf_8'):
        self.fin = open(fname, encoding=encoding)
        yield ''
        self.fin.close()

