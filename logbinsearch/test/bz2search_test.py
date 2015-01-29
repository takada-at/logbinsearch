# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import tempfile
import os
from .. import bz2search
from .. import bz2bin
from ..common import Comparator
def test_searchblock():
    sample = os.path.join(os.path.dirname(__file__), 'sample/sample.bz2')
    with open(sample) as fd:
        print("start")
        pos = bz2search.searchblock(fd, 5)
        print("end")
        assert pos > 0
        print(pos)
        print("start")
        rd = bz2search.BlockReader(fd, pos)
        print("end")
        assert rd
        line = rd.next()
        assert line
        print(len(line))
        print(line)
        assert "\n"==line[-1]

def test_binsearch():
    sample = os.path.join(os.path.dirname(__file__), 'sample/sample.bz2')
    comparator = Comparator(0, lower="333", upper="340")
    binsearch = bz2bin.BZ2BinSearch(sample, comparator)
    with binsearch as res:
        assert res
        results = [res.next() for i in range(100)]
        assert 100 == len(results)
        assert "333" <= results[0][0] < "340"
        print(results[:2])



