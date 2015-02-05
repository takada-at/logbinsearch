# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import os
import random
import bz2
from ..scripts import logdatetimesearch
from .. import binsearch

sample = os.path.join(os.path.dirname(__file__), 'sample/sample_datetime.bz2')

def generate(fromdate):
    if os.path.exists(sample):
        return sample

    bzf = bz2.BZ2File(sample, 'w', compresslevel=1)
    ptr = fromdate
    for i in range(100):
        for j in range(10):
            rows = [i*10 + j, ptr.strftime('%Y-%m-%d %H:%M:%S')] \
                + [random.randint(0, 100)]*10
            line = " ".join(map(bytes, rows)) + "\n"
            bzf.write(bytes(line))

        ptr += datetime.timedelta(minutes=random.randint(0, 10))

    return sample

def test_search():
    binsearch.DEBUG = 1
    results = []
    def mock(*string):
        #print(*string)
        results.append(string)

    fromdate = datetime.datetime(2015, 1, 20, 13, 0, 0)
    sample = generate(fromdate)
    logdatetimesearch.info = mock
    import sys
    sys.argv = ['logdatetimesearch.py', '-f', '2015-01-20 15:10:00', '-t', '2015-01-20 15:20:00', sample]
    logdatetimesearch.main()
    for row in results[1:10]:
        print(row)
        vals = row[0].split()
        vals = " ".join(vals[1:3])
        assert vals>='2015-01-20 15:10'
        assert vals<='2015-01-20 15:20'

    reload(logdatetimesearch)
    reload(sys)

