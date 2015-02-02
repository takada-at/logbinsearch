# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
from .. import bz2search
from .. import bz2bin
from ..binsearch import Comparator
def test_searchblock():
    sample = os.path.join(os.path.dirname(__file__), 'sample/sample.bz2')
    with open(sample) as fd:
        pos = bz2search.searchblock(fd, 5)
        assert pos > 0
        print(pos)
        rd = bz2search.BlockReader(fd, pos)
        assert rd
        line = rd.next()
        assert line
        print(len(line))
        print(line)
        assert "\n"==line[-1]
        # next block
        fd = open(sample)
        fd.seek(0)
        pos = bz2search.searchblock(fd, (pos+80)//8)
        print('pos',pos)
        rd = bz2search.BlockReader(fd, pos)
        assert rd
        line = rd.next()
        assert line
        print(len(line))
        print(line)
        assert "\n"==line[-1]


def test_binsearch():
    valtype = int
    sample = os.path.join(os.path.dirname(__file__), 'sample/sample.bz2')
    comparator = Comparator(0, lower=333, upper=334, valtype=valtype)
    binsearch = bz2bin.BZ2BinSearch(sample, comparator)
    with binsearch as res:
        assert res
        results = [res.next() for i in range(100)]
        print(results[:2])
        assert 100 == len(results)
        assert 333 <= int(results[0][0]) < 334
        print(results[:2])



