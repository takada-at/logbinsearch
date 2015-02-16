# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from . import bz2search
from .binsearch import BaseBinSearch

class BZ2BinSearch(BaseBinSearch):
    MINSIZE = 5000
    def __init__(self, filepath, comparator, reader):
        super(BZ2BinSearch, self).__init__(filepath, comparator, reader)
        self.prevblock = None
        self.fio = None
        self.blreader = None
    def _getblockreader(self, fio, binpos):
        if binpos < 0:
            return None

        if self.blreader is None:
            blreader = bz2search.BlockReader(fio, binpos)
            self.blreader = blreader
        else:
            self.blreader.reset(fio, binpos)
            blreader = self.blreader
        #skip 1 line
        try:
            blreader.next()
        except StopIteration:
            return None
        return blreader
    def _binsearch(self, filesize, fio, comparator, reader):
        if filesize <= self.MINSIZE:
            minsize = self.MINSIZE // filesize
        else:
            minsize = self.MINSIZE
        result = None
        half = filesize // 2
        start = 0
        size = half
        blreader = None
        # search block
        while size > minsize:
            binpos = bz2search.searchblock(fio, half)
            if(binpos<0) or \
                    (self.prevblock and self.prevblock == binpos):
                ## too large
                pass
            else:
                blreader = self._getblockreader(fio, binpos)
                if blreader:
                    result = self.try_compare(blreader, reader, comparator)
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
            blreader = self._getblockreader(fio, binpos)

        if blreader is None:
            return None

        if result==0:
            return self._iter_results(blreader)

        return self._binsearchinblock(blreader)
    def _binsearchinblock(self, blreader):
        while True:
            result = self.try_compare(blreader, self.reader, self.comparator)
            if result is None:
                return None
            if result == 0:
                return self._iter_results(blreader)
            # too large
            elif result < 0:
                return self._iter_results(blreader)
            else:
                continue


