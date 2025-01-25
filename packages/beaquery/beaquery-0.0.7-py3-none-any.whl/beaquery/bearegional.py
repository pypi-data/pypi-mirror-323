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
    argp = argparse.ArgumentParser(description='get BEA Regional data')
    argp.add_argument('--tn', required=True, help='table name')
    argp.add_argument('--fips', required=True,
                      help='geo fips')
    argp.add_argument('--lncd', required=True, help='line code')
    argp.add_argument('--yr', required=True,
                      help='year YYYY  X or all')

    argp.add_argument('--format', default='json',
                      choices=['json', 'XML'], help='result format')

    args=argp.parse_args()

    BN = beaqueryq.BEAQueryQ()
    d = BN.getRegionaldata(args.tn, args.fips, args.lncd, args.yr, args.format)
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
