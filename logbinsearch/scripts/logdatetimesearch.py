# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import argparse
from .. import create_searcher

def info(string):
    print(string)

def getresults(args):
    kw = dict(delimiter=args.delimiter, quotechar=args.quotechar, lower=args._from, upper=args.to)
    searcher = create_searcher(args.filepath, args.start, args.end, **kw)
    with searcher as result:
        for row in result:
            yield row

def search(args):
    info('## in {file} from {fromd} to {to}'.format(file=args.filepath, fromd=args._from, to=args.to))
    for row in getresults(args):
        info(args.delimiter.join(row))

def validatedatetime(args):
    try:
        fromd = datetime.datetime.strptime(args._from, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise ValueError('wrong datetime format {}'.format(args._from))

    if args.to is None:
        args.to = (fromd + datetime.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
    try:
        datetime.datetime.strptime(args.to, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise ValueError('wrong datetime format {}'.format(args._from))

    if args.prefix:
        args.to = args.prefix + args.to
        args._from = args.prefix + args._from

def main():
    parser = argparse.ArgumentParser(description='search bz2 accesslog')
    parser.add_argument('-s', '--start', default=1, type=int, help='start collumn')
    parser.add_argument('-e', '--end', default=2, type=int, help='end collumn')
    parser.add_argument('-f', '--from', dest='_from', help="From time for log reading / '%%Y-%%m-%%d %%H:%%M:%%S'n")
    parser.add_argument('-t', '--to', help="To time for log reading / '%%Y-%%m-%%d %%H:%%M:%%S'")
    parser.add_argument('-d', '--delimiter', help="log dalimiter", default=b" ", type=bytes)
    parser.add_argument('-q', '--quotechar', help="log quotecher", default=b"\"", type=bytes)
    parser.add_argument('-p', '--prefix', help="log collumn prefix", default=b"", type=bytes)
    parser.add_argument('filepath')
    args = parser.parse_args()
    args.delimiter = args.delimiter.replace(b"\\t", b"\t")
    validatedatetime(args)
    search(args)

if __name__=='__main__':
    main()


