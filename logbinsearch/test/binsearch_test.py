# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import bz2
import os
import tempfile
from ..binsearch import Comparator, TextBinSearch
from ..import binsearch
binsearch.DEBUG = 1
def test_TextBinSearch():
    sample = os.path.join(os.path.dirname(__file__), 'sample/sample.bz2')
    comparator = Comparator(0, lower=333, upper=334, valtype=int)
    with bz2.BZ2File(sample) as fio:
        with tempfile.NamedTemporaryFile('w') as out:
            out.write(fio.read())
            out.seek(0)
            with TextBinSearch(out.name, comparator) as res:
                results = [res.next() for i in range(100)]
                print(results[:2])
                assert 100 == len(results)
                assert 3 == len(results[0][0])
                assert 333 <= int(results[0][0]) < 340



