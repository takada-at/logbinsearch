# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import traceback
import os
import csv
class Comparator(object):
    def __init__(self, col, colupper=None, delimiter="\t", quotechar='"', 
                 comparefunc=None, lower=None, upper=None):
        self.col  = col
        if colupper is None or col >= colupper:
            colupper = col + 1

        self.colupper = colupper
        self.lower = lower
        self.upper = upper
        self.delimiter = bytes(delimiter)
        self.quotechar = bytes(quotechar)
        if comparefunc is None:
            comparefunc = self._compare_value
        self.comparefunc = comparefunc
    def make_parser(self, reader):
        return csv.reader(reader, delimiter=self.delimiter, quotechar=self.quotechar)
    def _compare_value(self, rows):
        lower = self.lower
        upper = self.upper
        val = self.delimiter.join(rows[self.col:self.colupper])
        if lower <= val < upper:
            return 0
        elif val >= upper:
            return -1
        return 1
    def compare(self, reader):
        self.buffer = []
        parser = self.make_parser(reader)
        self.parser = parser
        for i in range(30):
            try:
                rows = parser.next()
                res = self.comparefunc(rows)
                if res==0:
                    self.buffer.append(rows)
                return res
            except:
                print(traceback.format_exc())
                pass

        return None

class BaseBinSearch(object):
    def __init__(self, filepath, comparator):
        self.filepath = filepath
        self.comparator = comparator
        self.fio = None
    def __enter__(self):
        filesize = os.path.getsize(self.filepath)
        self.fio = open(self.filepath)
        return self._binsearch(filesize, self.fio, self.comparator)
    def __exit__(self, exc_type, exc_value, traceback):
        if self.fio:
            self.fio.close()
            self.fio = None

        if exc_value is None:
            return True
    def _binsearch(self, filesize, fio, comparator):
        raise NotImplementedError()
