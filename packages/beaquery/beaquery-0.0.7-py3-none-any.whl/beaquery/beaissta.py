#! env python
#

import argparse
import os
import sys
import webbrowser

try:
    from beaquery import beaqueryq
except Exception as e:
    import beaqueryq

def main():
    argp = argparse.ArgumentParser(description='get BEA IntlServSTA data')
    argp.add_argument('--chan', required=True, help='channel')
    argp.add_argument('--dest', required=True, help='destination')
    argp.add_argument('--indstry', required=True, help='industry')
    argp.add_argument('--aoc', required=True, help='area or country')
    argp.add_argument('--yr', required=True,
                      help='year YYYY  X or all')

    argp.add_argument('--format', default='json',
                      choices=['json', 'XML'], help='result format')

    args=argp.parse_args()

    BN = beaqueryq.BEAQueryQ()
    d = BN.getIntlServSTAdata(args.chan, args.dest, args.indstry,
                              args.aoc, args.yr, args.format)
    if d == None:
        print('no output', file=sys.stderr)
    else:
        if type(d) == type({}):
            csv = BN.dd2csv(d)
            print(csv)
        elif type(d) == type([]):
            for i in range(len(d)):
                print('\n\n')
                csv = BN.dd2csv(d[i])
                print(csv)
if __name__ == '__main__':
    main()
