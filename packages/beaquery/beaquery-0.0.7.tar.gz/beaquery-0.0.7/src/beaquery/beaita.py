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
    argp = argparse.ArgumentParser(description='get BEA ITA data')
    argp.add_argument('--indctr', required=True, help='ITA indicator')
    argp.add_argument('--aoc', required=True, help='ITA area or country')
    argp.add_argument('--freq', required=True,
                     help='frequency M, Q, A or comma separated list')
    argp.add_argument('--yr', required=True,
                      help='year YYYY  X or all')

    argp.add_argument('--format', default='json',
                      choices=['json', 'XML'], help='result format')

    args=argp.parse_args()

    BN = beaqueryq.BEAQueryQ()
    d = BN.getITAdata(args.indctr, args.aoc, args.freq, args.yr, args.format)
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
