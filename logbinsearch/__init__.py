# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
from .binsearch import Reader, Comparator, TextBinSearch
from .bz2bin import BZ2BinSearch

def create_searcher(filepath, col, colupper=None, delimiter=b"\t", quotechar=b"\"", valtype=str, lower=None, upper=None, ext=None):
    if not os.path.exists(filepath):
        raise Exception('cannot found: {}'.format(filepath))

    if ext is None:
        base, ext = os.path.splitext(filepath)

    if ext=='.bz2':
        searcher = BZ2BinSearch
    else:
        searcher = TextBinSearch

    reader = Reader(col, colupper, delimiter, quotechar, valtype)
    comparator = Comparator(lower, upper)
    return searcher(filepath, comparator, reader)


