# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import bz2
import os
import tempfile
from .. import create_searcher
from ..import binsearch
binsearch.DEBUG = 1
def test_TextBinSearch():
    sample = os.path.join(os.path.dirname(__file__), 'sample/sample.bz2')
    
    with bz2.BZ2File(sample) as fio:
        with tempfile.NamedTemporaryFile('w') as out:
            out.write(fio.read())
            out.seek(0)
            searcher =  create_searcher(out.name, 0, lower=333, upper=334, valtype=int)
            with searcher as res:
                results = list(res)
                print(results[:2])
                assert 2 == len(results)
                assert 3 == len(results[0][0])
                assert 333 <= int(results[0][0]) < 334



