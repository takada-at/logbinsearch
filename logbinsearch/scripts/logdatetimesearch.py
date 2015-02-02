# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import os
import argparse
from .. import binsearch
from .. import bz2bin

def getresults(args):
    if not os.path.exists(args.filepath):
        raise Exception('cannot found: {}'.format(args.filepath))

    base, ext = os.path.splitext(args.filepath)
    if ext=='.bz2':
        searcher = bz2bin.BZ2BinSearch
    else:
        searcher = binsearch.TextBinSearch

    kw = dict(delimiter=args.delimiter, quotechar=args.quotechar, lower=args._from, upper=args.to)
    comparator = binsearch.Comparator(args.start, args.end, **kw)
    with searcher(args.filepath, comparator) as result:
        for row in result:
            yield row

def search(args):
    print('## in {file} from {fromd} to {to}'.format(file=args.filepath, fromd=args._from, to=args.to))
    for row in getresults(args):
        print(args.delimiter.join(row))

def validatedatetime(args):
    try:
        fromd = datetime.datetime.strptime(args._from, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise ValueError('wrong datetime format {}'.format(args._from))

    if args.to is None:
        args.to = (fromd + datetime.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
    try:
        tod = datetime.datetime.strptime(args.to, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise ValueError('wrong datetime format {}'.format(args._from))
def main():
    parser = argparse.ArgumentParser(description='search bz2 accesslog')
    parser.add_argument('-s', '--start', default=1, type=int, help='start collumn')
    parser.add_argument('-e', '--end', default=2, type=int, help='end collumn')
    parser.add_argument('-f', '--from', dest='_from', help="From time for log reading / '%Y-%m-%d %H:%M:%S'n")
    parser.add_argument('-t', '--to', help="To time for log reading / '%Y-%m-%d %H:%M:%S'")
    parser.add_argument('-d', '--delimiter', help="log dalimiter", default=b" ")
    parser.add_argument('-q', '--quotechar', help="log quotecher", default=b"\"")
    parser.add_argument('filepath')
    args = parser.parse_args()
    validatedatetime(args)
    search(args)

if __name__=='__main__':
    main()


