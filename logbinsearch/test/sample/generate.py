# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import bz2
import os
import random
dirname = os.path.dirname(__file__)
filepath = os.path.join(dirname, 'sample.bz2')
with bz2.BZ2File(filepath, 'w', compresslevel=1) as fd:
    for i in range(1000):
        vals = [j for j in range(100)]
        fd.write("\t".join(map(str, vals)) + "\n")




