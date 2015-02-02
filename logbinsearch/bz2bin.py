# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from . import bz2search
from .binsearch import BaseBinSearch

class BZ2BinSearch(BaseBinSearch):
    MINSIZE = 5000
    def __init__(self, filepath, comparator):
        self.filepath = filepath
        self.comparator = comparator
        self.prevblock = None
        self.fio = None
    def _getblockreader(self, fio, binpos):
        if binpos < 0:
            return None
        reader = bz2search.BlockReader(fio, binpos)
        #skip 1 line
        try:
            reader.next()
        except StopIteration:
            print("stop ", binpos)
            return None
        return reader
    def _binsearch(self, filesize, fio, comparator):
        if filesize <= self.MINSIZE:
            minsize = self.MINSIZE // filesize
        else:
            minsize = self.MINSIZE
        result = None
        half = filesize // 2
        start = 0
        size = half
        reader = None
        # search block
        while size > minsize:
            binpos = bz2search.searchblock(fio, half)
            if(binpos<0) or \
                    (self.prevblock and self.prevblock == binpos):
                ## too large
                pass
            else:
                reader = self._getblockreader(fio, binpos)
                if reader:
                    result = comparator.compare(reader)
                    if result is None: #error
                        return None
                    if result == 0: #found
                        #result.reset()
                        break
                    elif result < 0:
                        #too large
                        pass
                    else:
                        #too small
                        start = half

            #print("b pos", binpos, self.prevblock, result, start, half, size)
            self.prevblock = binpos
            size = size // 2
            half = start + size

        #print("res", start, half, size)
        if size <= minsize and result < 0:
            binpos = bz2search.searchblock(fio, 0)
            reader = self._getblockreader(fio, binpos)

        if reader is None:
            return None

        if result==0:
            return comparator.results()
        return self._binsearchinblock(comparator, reader)
    def _binsearchinblock(self, comparator, reader):
        while True:
            result = comparator.compare(reader)
            if result is None:
                return None
            if result == 0:
                return comparator.results()
            # too large
            elif result < 0:
                return comparator.results()
            else:
                continue


