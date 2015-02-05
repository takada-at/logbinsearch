# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
from .. import bz2search
from .. import bz2bin
from .. import create_searcher

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
        rd = None
        rd = bz2search.BlockReader(fd, pos)
        assert rd
        line = rd.next()
        assert line
        assert "\n"==line[-1]
        fd2 = open(sample)
        rd.reset(fd2, pos)
        assert rd
        line = rd.next()
        assert line
        assert "\n"==line[-1]

def test_binsearch():
    valtype = int
    sample = os.path.join(os.path.dirname(__file__), 'sample/sample.bz2')
    binsearch = create_searcher(sample, 0,
                                lower=333, upper=334, valtype=valtype)
    with binsearch as res:
        assert res
        results = list(res)
        print(results[:2])
        assert 2 == len(results)
        assert 333 <= int(results[0][0]) <= 334
        assert 333 <= int(results[1][0]) <= 334
        print(results[:2])



