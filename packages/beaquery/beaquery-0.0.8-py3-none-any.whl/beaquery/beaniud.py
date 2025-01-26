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
    argp = argparse.ArgumentParser(description='get BEA NIUnderlyingDetail'
                                   ' data')
    argp.add_argument('--dataset', default='NIUnderlyingDetail')
    argp.add_argument('--tn', required=True,
                      help='NIUnderlyingDetail table name')
    argp.add_argument('--freq', required=True,
                     help='frequency M, Q, A or comma separated list')
    argp.add_argument('--yr', required=True,
                      help='year YYYY  X or all')

    argp.add_argument('--format', default='json',
                      choices=['json', 'XML'], help='result format')

    argp.add_argument('--csvfn', \
         help='name of file to store dataset CSV result')

    argp.add_argument('--splitkey', default='LineDescription',
        help='table column name to use to split the table')
    argp.add_argument('--xkey', default='TimePeriod',
        help='table column name to use to plot the data')
    argp.add_argument('--ykey', default='DataValue',
        help='table column name to use to plot the data')
    argp.add_argument('--unitskey', default='METRIC_NAME',
        help='table column name to use to label the data')
    argp.add_argument('--htmlfn', \
        help='name of file to store dataset HTML result')

    args=argp.parse_args()

    BN = beaqueryq.BEAQueryQ()
    d = BN.getNIUnderlyingDetaildata(args)
    if d == None:
        print('%s: no data' % os.path.basename(__file__), file=sys.stderr)
        sys.exit(1)
    else:
        if args.csvfn != None:
            BN.store2csv(d, args.csvfn)
        elif args.htmlfn != None:
            h = BN.d2html(d, args)
            with open(args.htmlfn, 'w') as fp:
                print(h, file=fp)
            webbrowser.open('file://%s' % args.htmlfn)
        else:
            BN.print2csv(d)


if __name__ == '__main__':
    main()
