# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import csv
import itertools
import os
import traceback
DEBUG = 1
TRY_TIMES = 30
class Comparator(object):
    def __init__(self, col, colupper=None, delimiter=b"\t", quotechar=b"\"",
                 comparefunc=None, lower=None, upper=None, valtype=str):
        self.col  = col
        if colupper is None or col > colupper:
            colupper = col
        if comparefunc is None:
            comparefunc = self._compare_value
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.colupper = colupper + 1
        self.lower = lower
        self.upper = upper
        self.valtype = valtype
        self.comparefunc = comparefunc
    def make_parser(self, reader):
        return csv.reader(reader, delimiter=self.delimiter, quotechar=self.quotechar)
    def _compare_value(self, rows):
        lower = self.lower
        upper = self.upper
        val = self.valtype(self.delimiter.join(rows[self.col:self.colupper]))
        #print(lower, val, upper)
        if lower <= val < upper:
            return 0
        elif val >= upper:
            return -1
        return 1
    def compare(self, reader):
        self.buffer = []
        parser = self.make_parser(reader)
        self.parser = parser
        for i in range(TRY_TIMES):
            try:
                rows = parser.next()
                res = self.comparefunc(rows)
                if res==0:
                    self.buffer.append(rows)
                return res
            except StopIteration:
                return None
            except:
                if DEBUG:
                    print(traceback.format_exc())

        return None
    def results(self):
        return itertools.chain(self.buffer, self.parser)
    def __repr__(self):
        s = self
        return "Comparator<{}:{} '{}' {}--{}>".format(s.col, s.colupper, s.delimiter,
                                                     s.lower, s.upper)

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

class TextBinSearch(BaseBinSearch):
    def _binsearch(self, filesize, fio, comparator):
        half = filesize // 2
        start = 0
        size = half
        while size > 100:
            fio.seek(half)
            fio.next()
            result = comparator.compare(fio)
            if result is None:
                return None
            if result==0: #in
                break
            elif result < 0:
                pass
            else:
                start = half

            size = size // 2
            half = start + size

        return comparator.results()
