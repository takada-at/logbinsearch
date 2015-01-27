# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import tempfile
import os
from .. import bz2search
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
        print(rd.next())
