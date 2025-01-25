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
    argp = argparse.ArgumentParser(description='get BEA MNE data')
    argp.add_argument('--sid', required=True, help='MNE series id')
    argp.add_argument('--doi', help='direction of investment')
    argp.add_argument('--cls', help='classification')
    argp.add_argument('--cnt', help='country')
    argp.add_argument('--indstry', help='industry')
    argp.add_argument('--yr', required=True,
                      help='year YYYY  X or all')

    argp.add_argument('--format', default='json',
                      choices=['json', 'XML'], help='result format')

    args=argp.parse_args()

    BN = beaqueryq.BEAQueryQ()
    d = BN.getMNEdata(args.sid, args.doi, args.cls, args.cnt,
                               args.indstry, args.yr, args.format)
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
