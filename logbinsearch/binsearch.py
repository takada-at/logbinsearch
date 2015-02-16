# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import csv
import os
import traceback
DEBUG = 1
TRY_TIMES = 30


class Reader(object):
    def __init__(self, col, colupper=None, delimiter=b"\t", quotechar=b"\"", valtype=str):
        self.col  = col
        if colupper is None or col > colupper:
            colupper = col
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.colupper = colupper + 1
        self.valtype = valtype
    def setfile(self, fileobj):
        self.parser = csv.reader(fileobj, delimiter=self.delimiter, quotechar=self.quotechar)
        return self.parser
    def __iter__(self):
        return self
    def get_value(self, rows):
        return self.valtype(self.delimiter.join(rows[self.col:self.colupper]))
    def next(self):
        row = self.parser.next()
        val = self.get_value(row)
        return val, row

class Comparator(object):
    def __init__(self, lower=None, upper=None):
        self.lower = lower
        self.upper = upper
    def compare(self, val):
        lower = self.lower
        upper = self.upper
        if lower <= val <= upper:
            return 0
        elif val > upper:
            return -1
        return 1
    def __repr__(self):
        return "Comparator({}, {})".format(repr(self.lower), repr(self.upper))

class BaseBinSearch(object):
    def __init__(self, filepath, comparator, reader):
        self.filepath   = filepath
        self.comparator = comparator
        self.reader     = reader
        self.fio        = None
        self.buffer     = []
    def __enter__(self):
        filesize = os.path.getsize(self.filepath)
        self.fio = open(self.filepath)
        return self._binsearch(filesize, self.fio, self.comparator, self.reader)
    def __exit__(self, exc_type, exc_value, traceback):
        if self.fio:
            self.fio.close()
            self.fio = None

        if exc_value is None:
            return True
    def try_compare(self, fio, reader, comparator):
        parser = reader.setfile(fio)
        for i in range(TRY_TIMES):
            try:
                row = parser.next()
                val = reader.get_value(row)
                res = comparator.compare(val)
                if res==0:
                    self.buffer.append(row)
                return res
            except StopIteration:
                return None
            except:
                if DEBUG:
                    print(traceback.format_exc())

        return None
    def _iter_results(self, input_):
        if not self.buffer:
            raise StopIteration()

        for row in self.buffer:
            yield row

        self.reader.setfile(input_)
        comparator = self.comparator
        for val, row in self.reader:
            res = comparator.compare(val)
            if res == 0:
                yield row
            else:
                break

    def _binsearch(self, filesize, fio, comparator, reader):
        raise NotImplementedError()

class TextBinSearch(BaseBinSearch):
    def _binsearch(self, filesize, fio, comparator, reader):
        half = filesize // 2
        start = 0
        size = half
        while size > 100:
            fio.seek(half)
            fio.next()

            result = self.try_compare(fio, reader, comparator)
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

        return self._iter_results(fio)
