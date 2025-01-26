
#! env python
#
import argparse
import json
import os
import sys
import time
import webbrowser
import xml
import xml.etree.ElementTree as ET

import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go

try:
    from beaquery import ebquery
except Exception as e:
    import ebquery


class BEAQueryQ():
    def __init__(self):

        self.bsurl = 'https://apps.bea.gov/api/signup/'
        if 'BEA_API_KEY' in os.environ:
                self.api_key = os.environ['BEA_API_KEY']
        else:
            print('BEA api_key required: %s' % (self.bsurl), file=sys.stderr)
            print('assign this key to BEA_API_KEY env variable',
                              file=sys.stderr)
            sys.exit()

        self.bdurl = 'https://apps.bea.gov/api/data/'
        self.burl = '%s?&UserID=%s' % (self.bdurl, self.api_key)

        self.trurl = 'https://apps.bea.gov/national/Release/TXT/TablesRegister.txt'

        self.uq = ebquery._EBURLQuery()

        self.args = None

    def getNIPAregister(self):
        """ getNIPAregister()
        retrieve and return the register of BEA NIPA tables
        """
        resp = self.uq.query(self.trurl)
        if resp == None:
            print('getNIPAregister: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        return rstr

    # not using TableID Parameter
    def NIPAParams(self, args):
        if args.freq == None or args.yr == None:
            print('NIPAParams: Frequency and Year required', file=sys.stderr)
            sys.exit()
        params = ('&method=GetData&'
                  'DatasetName=%s&'
                  'TableName=%s&'
                  'ShowMillions=%s&'
                  'Frequency=%s&'
                  'Year=%s&'
                  'ResultFormat=%s' %
                  ('NIPA', args.tn, args.showm, args.freq, args.yr,
                  args.format) )
        return params

    def NIUnderlyingDetailParams(self, args):
        if args.freq == None or args.yr == None:
            print('NIUnderlyingDetailParams: Frequency and Year required',
                   file=sys.stderr)
            sys.exit()
        params = ('&method=GetData&'
                  'DatasetName=%s&'
                  'TableName=%s&'
                  'Frequency=%s&'
                  'Year=%s&'
                  'ResultFormat=%s' %
                  ('NIUnderlyingDetail', args.tn, args.freq, args.yr,
                  args.format) )
        return params


    def MNEParameters(self, args):
        if args.doi == None or args.cls == None or args.yr == None:
            print('MNEParameters: DirectionOfInvestment,'
                  'Classification,and Year required', file=sys.stderr)
            sys.exit()
        params = ('&method=GetData&'
                  'DatasetName=%s&'
                  'SeriesID=%s&'
                  'DirectionOfInvestment=%s&'
                  'Classification=%s&'
                  'Country=%s&'
                  'Industry=%s&'
                  'Year=%s&'
                  'ResultFormat=%s' %
                  ('MNE', args.sid, args.doi, args.cls, args.cnt,
                  args.indstry, args.yr, args.format) )
        return params

    def FixedAssetsParameters(self, args):
        if args.tn == None or args.yr == None:
            print('FixedAssetsParameters TableName and Year required',
                  file=sys.stderr)
            sys.exit()
        params = ('&method=GetData&'
                  'DatasetName=%s&'
                  'TableName=%s&'
                  'Year=%s&'
                  'ResultFormat=%s' %
                  ('FixedAssets', args.tn, args.yr, args.format) )
        return params

    def ITAParameters(self, args):
        params = ('&method=GetData&'
                  'DatasetName=%s&'
                  'Indicator=%s&'
                  'AreaOrCountry=%s&'
                  'Frequency=%s&'
                  'Year=%s&'
                  'ResultFormat=%s' %
                  ('ITA', args.indctr, args.aoc, args.freq, args.yr,
                  args.format) )
        return params

    def IIPParameters(self, args):
        params = ('&method=GetData&'
                  'DatasetName=%s&'
                  'TypeOfInvestment=%s&'
                  'Component=%s&'
                  'Frequency=%s&'
                  'Year=%s&'
                  'ResultFormat=%s' %
                  ('IIP', args.toi, args.comp, args.freq, args.yr,
                  args.format) )
        return params

    def InputOutputParameters(self, args):
        if args.tid == None or args.yr == None:
            print('InputOutputParameters TableID and Year required',
                  file=sys.stderr)
            sys.exit()
        params = ('&method=GetData&'
                  'DatasetName=%s&'
                  'TableID=%s&'
                  'Year=%s&'
                  'ResultFormat=%s' %
                  ('InputOutput', args.tid, args.yr, args.format) )
        return params

    def IntlServTradeParameters(self, args):
        params = ('&method=GetData&'
                  'DatasetName=%s&'
                  'TypeOfService=%s&'
                  'TradeDirection=%s&'
                  'Affiliation=%s&'
                  'AreaOrCountry=%s&'
                  'Year=%s&'
                  'ResultFormat=%s' %
                  ('IntlServTrade', args.tos, args.tdir, args.affl,
                  args.aoc, args.yr, args.format) )
        return params

    def IntlServSTAParameters(self, args):
        params = ('&method=GetData&'
                  'DatasetName=%s&'
                  'Channel=%s&'
                  'Destination=%s&'
                  'Industry=%s&'
                  'AreaOrCountry=%s&'
                  'Year=%s&'
                  'ResultFormat=%s' %
                  ('IntlServSTA', args.chan, args.dest, args.indstry,
                  args.aoc, args.yr, args.format) )
        return params

    def GDPbyIndustryParameters(self, args):
        if args.freq == None or args.indstry == None or args.tid == None \
        or args.yr == None:
            print('GDPbyIndustryParameters Frequency, Industry,'
            'TableID, Year required', file=sys.stderr)
            sys.exit()
        params = ('&method=GetData&'
                  'DatasetName=%s&'
                  'TableID=%s&'
                  'Industry=%s&'
                  'Frequency=%s&'
                  'Year=%s&'
                  'ResultFormat=%s' %
                  ('GDPbyIndustry', args.tid, args.indstry, args.freq,
                  args.yr, args.format) )
        return params

    def RegionalParameters(self, args):
        if args.fips == None or args.tn == None or args.lncd == None:
            print('Regional GeoFips, LineCode, TableName required',
                  file=sys.stderr)
            sys.exit()
        params = ('&method=GetData&'
                  'DatasetName=%s&'
                  'GeoFIPS=%s&'
                  'TableName=%s&'
                  'LineCode=%s&'
                  'Year=%s&'
                  'ResultFormat=%s' %
                  ('Regional', args.fips, args.tn, args.lncd, args.yr,
                  args.format) )
        return params

    def UnderlyingGDPbyIndustryParameters(self, args):
        if args.freq == None or args.indstry == None or args.tid == None or \
           args.yr == None:
            print('UnderlyingGDPbyIndustryParameters TableID, Industry,'
                  'Frequency, Year required', file=sys.stderr)
            sys.exit()
        params = ('&method=GetData&'
                  'DatasetName=%s&'
                  'TableID=%s&'
                  'Industry=%s&'
                  'Frequency=%s&'
                  'Year=%s&'
                  'ResultFormat=%s' %
                  ('UnderlyingGDPbyIndustry', args.tid, args.indstry,
                  args.freq, args.yr, args.format) )
        return params

# dict_keys(['TableName', 'SeriesCode', 'LineNumber', 'LineDescription', 'TimePeriod', 'METRIC_NAME', 'CL_UNIT', 'UNIT_MULT', 'DataValue', 'NoteRef'])
#
# {'TableName': 'FAAt101', 'SeriesCode': 'k1ttotl1es00', 'LineNumber': '2', 'LineDescription': 'Fixed assets', 'TimePeriod': '1926', 'METRIC_NAME': 'Current Dollars', 'CL_UNIT': 'Level', 'UNIT_MULT': '6', 'DataValue': '270,574', 'NoteRef': 'FAAt101'}

    def getNIPAdata(self, args):
        """ getNIPAdata(tn, fq, yr, fmt)
        tn - table name
        fq - frequency
        yr - year
        shm - show millions
        fmt - result format
        retrieve national income and product accounts data
        """
        params = self.NIPAParams(args)
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('GetNIPAdata: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        jsd = json.loads(rstr)
        return jsd['BEAAPI']['Results']

    def getNIUnderlyingDetaildata(self, args):
        """ getNIUnderlyingDetaildata(tn, fq, yr, fmt)
        tn - table name
        fq - frequency
        yr - year
        fmt - result format
        retrieve national income underlying detail  data
        """
        params = self.NIUnderlyingDetailParams(args)
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('getNIUnderlyingDetaildata: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        jsd = json.loads(rstr)
        return jsd['BEAAPI']['Results']

# dict_keys(['Year', 'SeriesID', 'SeriesName', 'Row', 'ColumnGParent', 'ColumnParent', 'Column', 'RowCode', 'ColumnCode', 'ColumnParentCode', 'ColumnGParentCode', 'TableScale', 'DataValueUnformatted', 'TableColumnDisplayOrder', 'TableRowDisplayOrder', 'DataValue'])
# {'Year': '2012', 'SeriesID': '26', 'SeriesName': 'Debt Instruments Inflows', 'Row': 'Germany', 'ColumnGParent': 'None', 'ColumnParent': 'Manufacturing', 'Column': 'Total Manufacturing', 'RowCode': '308', 'ColumnCode': '3000', 'ColumnParentCode': '3000', 'ColumnGParentCode': '0', 'TableScale': 'Millions of Dollars', 'DataValueUnformatted': '-5422', 'TableColumnDisplayOrder': '2.00', 'TableRowDisplayOrder': '10.00', 'DataValue': '-5,422'}

    def getMNEdata(self, args):
        """ getMNEdata(doi, cl, ind, cnt, yr, fmt)
        sid - series id
        doi - direction of investment
        cl - classification
        ind - industry
        cnt - country
        yr  - yr
        fmt - result format
        return multinational enterprises data
        """
        params = self.MNEParameters(args)
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('getMNEdata: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        jsd = json.loads(rstr)
        return jsd['BEAAPI']['Results']

    def getFixedAssetsdata(self, args):
        """ getFixedAssetsdata()
        tn - table name
        yr  - yr
        fmt - result format
        return fixed assets data
        """
        params = self.FixedAssetsParameters(args)
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('getFixedAssetsdata: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        jsd = json.loads(rstr)
        return jsd['BEAAPI']['Results']

    def getITAdata(self, args):
        """ getITAdata(ind, area, fq, yr, fmt)
        tn - table name
        yr  - yr
        fmt - result format
        return international transactions accounts data
        """
        params = self.ITAParameters(args)
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('getITAdata: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        jsd = json.loads(rstr)
        return jsd['BEAAPI']['Results']

    def getIIPdata(self, args):
        """ getIIPdata(ind, area, fq, yr, fmt)
        toi - type of investment
        cmp - component
        fq - frequency
        yr  - yr
        fmt - result format
        return international investment position data
        """
        params = self.IIPParameters(args)
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('getIIPdata: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        jsd = json.loads(rstr)
        return jsd['BEAAPI']['Results']

    def getInputOutputdata(self, args):
        """ getInputOutputdata(tid, yr, fmt)
        tid - table id
        yr- year
        fmt - result format
        return input output data
        """
        params = self.InputOutputParameters(args)
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('getInputOutputtdata: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        jsd = json.loads(rstr)
        return jsd['BEAAPI']['Results']

    def getIntlServTradedata(self, args):
        """ getIntlServTradedata(ind, tos, td, aff, area, yr, fmt)
        tos - type of service
        td - trade direction
        aff - affiliation
        area - area or country
        yr  - yr
        fmt - result format
        return international service trade data
        """
        params = self.IntlServTradeParameters(args)
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('getIntlServTradedata: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        jsd = json.loads(rstr)
        return jsd['BEAAPI']['Results']

    def getIntlServSTAdata(self, args):
        """ getIntlServSTAPdata( ch, dst, ind, area, yr, fmt)
        ch - channel
        dst - destination
        aff - affiliation
        ind - industry
        area - area or country
        yr  - yr
        fmt - result format
        return international services supplied through affiliates data
        """
        params = self.IntlServSTAParameters(args)
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('getIntlServSTAdata: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        jsd = json.loads(rstr)
        return jsd['BEAAPI']['Results']

    def getGDPbyIndustrydata(self, args):
        """ getGDPbyIndustrydata( ch, dst, ind, area, yr, fmt)
        tid = table id
        ind - industry 
        fq - frequency
        yr  - yr
        fmt - result format
        return gdp by industry data
        """
        params = self.GDPbyIndustryParameters(args)
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('getGDPbyIndustrydata: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        jsd = json.loads(rstr)
        return jsd['BEAAPI']['Results']

    def getRegionaldata(self, args):
        """ getRegionaldata(tn, lc, fips, yr, fmt)
        tn - table name
        lc - line code
        fips - geo fips code
        yr  - yr
        fmt - result format
        return regional data
        """
        params = self.RegionalParameters(args)
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('getRegionaldata: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        jsd = json.loads(rstr)
        return jsd['BEAAPI']['Results']

    def getUnderlyingGDPbyIndustrydata(self, args):
        """ getUnderlyingGDPbyIndustrydata(tid, ind, fq, yr, fmt)
        tid - table id
        ind - industry
        fq - frequency
        yr  - yr
        fmt - result format
        return underlying gdp by industry data
        """
        params = self.UnderlyingGDPbyIndustryParameters(args)
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('getRegionaldata: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        jsd = json.loads(rstr)
        return jsd['BEAAPI']['Results']

    def dd2csv(self, jsd):
        """ dd2csv(jsd)
        jsd - results from BEA table query
        return csv text for table data
        """
        if 'Data' not in jsd.keys():
            print('dd2csv no Data key', file=sys.stderr)
            print(jsd, file=sys.stderr)
            return None
        aa = self.dd2aa(jsd, 'Data')
        csv = self.aa2csv(aa)
        return csv

    def store2csv(self, d, fn):
        """store2csv(d, fn)
        d - results from table query
        fn - where to store the csv data
        """
        if type(d) == type({}):
            csv = self.dd2csv(d)
            with open(fn, 'w') as fp:
                print(csv, file=fp)
        elif type(d) == type([]):
            if not fn.endswith('csv'):
                print('csv filename must end with ".csv"', file=sys.stderr)
            for i in range(len(d)):
                csv = self.dd2csv(d[i])
                nfn = fn.replace('.csv', '%d.csv' % i)
                with open(fn, 'w') as fp:
                    print(csv, file=fp)

    def print2csv(self, d):
        """print2csv(d)
        d - results of table query
        print csv result to stdout
        """
        if type(d) == type({}):
            csv = self.dd2csv(d)
            print(csv)
        elif type(d) == type([]):
            for i in range(len(d)):
                print('\n\n\n')
                csv = self.dd2csv(d[i])
                print(csv)

    def paa2plots(self, parts, xk, yk, uk, t):
        """ paa2plots(self, aa, x, y, sk, t)
        parts - plot aa parts
        xk - key to x axis data
        yk - key to y axis data
        uk - key to y axis units
        t - plot title
        return plot figure for data in parts
        """
        fig  = make_subplots(shared_yaxes=True, shared_xaxes=True)
        xi = yi = ui = None

        units = None
        for k in parts.keys():
            aa = parts[k]
            if xi == None:
                for i in range(len(aa[0])):
                    if aa[0][i] == xk:
                        xi = i
                    elif aa[0][i] == yk:
                        yi = i
                    elif aa[0][i] == uk:
                        ui = i

            if uk.endswith('?'):
                units = uk
            if units == None:
                units = aa[1][ui]
            xa = []
            ya = []
            for i in range(1, len(aa)):
                xa.append(aa[i][xi])
                ya.append(aa[i][yi])
            fig.add_trace( go.Scatter(x=xa, y=ya, name=k))

        fig.update_layout(
            title=t,
            yaxis_title=units,
            xaxis_title='Date',
        )
        return fig


    def aa2plot(self, aa, xi, yi, ui, t):
        """ aa2plot(self, aa, x, y, t)
        aa - array of arrays
        xi - x index
        yi - y index
        ui - index to units
        t - plot title
        return plot figure
        """
        print('aa2plot add units', file =sys.stderr)
        fig  = make_subplots(shared_yaxes=True, shared_xaxes=True)

        xa = []
        ya = []
        units = aa[1][ui]
        for i in range(len(aa)):
            xa.append(aa[i][xi])
            ya.append(aa[i][yi])

        fig.add_trace( go.Scatter(x=xa, y=ya, name=t))

        fig.update_layout(
            title=t,
            yaxis_title=units,
            xaxis_title='Date',
        )
        return fig

    def aa2table(self, cap, aa):
       """ aa2table(aa)

       convert array of arrays to an html table
       aa - array of arrays
       """
       tbla = []
       # table
       tbla.append('<table border="1">')
       # table header
       hdra = aa[0]
       hdr = '</th><th>'.join(hdra)
       tbla.append('<tr><th scope="col">%s</th></tr>' % (hdr) )
       cap = '<caption>%s</caption>' % cap
       tbla.append(cap)
       # table rows
       for i in range(1, len(aa) ):
           rowa = aa[i]
           for j in range(len(rowa)):
               if rowa[j] == None:
                   rowa[j] = ''
               elif type(rowa[j]) == type(1):
                   rowa[j] = '%d' % rowa[j]
           row = '</td><td>'.join(rowa)
           tbla.append('<tr><td>%s</td></tr>' % (row) )

       # close
       tbla.append('</table>')
       return tbla


    def x2aa(self, dss, jsk):
        """ x2dict(dss)
        dss - string containing XML
        convert string result to array of arrays
        """
        root = ET.fromstring(dss)
        keys = []
        aa = []
        for c in root:
            for gc in c:
                if c.tag == 'Results':
                    print(c.tag, c.attrib, gc.tag, gc.attrib)
                    if len(aa) == 0:
                        keys = [k for k in gc.attrib.keys()]
                        aa.append(keys)
                    a = []
                    for k in keys:
                        a.append(gc.attrib[k])
                    aa.append(a)
        return aa


    def dd2aa(self, dsd, jsk):
        """ dd2aa(dss)
        dss - string containing json
        convert string result to array of arrays
        """
        if type(dsd[jsk]) == type({}):
            keys = [k for k in dsd[jsk].keys()]
            aa = []
            aa.append(keys)
            a = []
            d = dsd[jsk]
            for k in keys:
                if k not in d:
                    a.append('')
                else:
                    a.append(d[k])
            aa.append(a)
            return aa
        elif type(dsd[jsk]) == type([]):
            keys = [k for k in dsd[jsk][0].keys()]
            aa = []
            for d in dsd[jsk]:
                if len(aa) == 0:
                    aa.append(keys)
                a = []
                for k in keys:
                    if k not in d:
                        a.append('')
                    else:
                        a.append(d[k])
                aa.append(a)
            return aa
        else:
            print('dd2aa type error', file=sys.stderr)
            return None

    def js2aa(self, dss, jsk):
        """ js2aa(dss)
        dss - string containing json
        convert string result to array of arrays
        """
        dsd = json.loads(dss)

        if type(dsd['BEAAPI']['Results'][jsk]) != type([]):
            keys = [k for k in dsd['BEAAPI']['Results'][jsk].keys()]
            aa = []
            aa.append(keys)
            a = []
            for k in keys:
                a.append(dsd['BEAAPI']['Results'][jsk][k])
            aa.append(a)
            return aa


        keys = [k for k in dsd['BEAAPI']['Results'][jsk][0].keys()]
        aa = []
        for d in dsd['BEAAPI']['Results'][jsk]:
            if len(aa) == 0:
                aa.append(keys)
            a = []
            for k in keys:
                if k not in d:
                    a.append('')
                else:
                    if d[k].endswith(' '):
                        d[k] = d[k][0:-1]
                    a.append(d[k])
            aa.append(a)
        return aa

    def aasplit(self, aa, k):
        """ aasplit(self, aa, k)
        aa - array of arrays
        k - split key
        return split aa
        """
        ai = None # index to split key
        asp = {}
        asp['parts'] = {}
        keys = aa[0]
        for i in range(len(aa[0])):
            if aa[0][i] == k:
                ai = i
                break
        if ai == None:
            print('aasplit no key %s' % k, file=sys.stderr)
            sys.exit()
        for j in range(1, len(aa)):
            if aa[j][ai] not in asp['parts']:
                asp['parts'][aa[j][ai]] = []
                asp['parts'][aa[j][ai]].append(keys)
            asp['parts'][aa[j][ai]].append(aa[j])

        return asp

    def ds2uk(self, args):
        """ds2dn(args)
        args - command arguments
        return y axis units key
        """
        if args.dataset in ['NIPA', 'NIUnderlyingDetail', 'FixedAssets']:
            uk = 'METRIC_NAME'
        elif args.dataset in ['InputOutput']:
            uk = 'ColType'
        elif args.dataset in ['GDPbyIndustry', 'UnderlyingGDPbyIndustry']:
            uk = 'Billions?'
        elif args.dataset in ['MNE']:
            uk = 'TableScale'
        elif args.dataset in ['IIP', 'Regional']:
            uk = 'CL_UNIT'
        elif args.dataset in ['ITA', 'IntlServTrade', 'IntlServSTA']:
            uk = 'CL_UNIT'
        else:
            return None
        return uk

    def ds2xk(self, args):
        """ds2dn(args)
        args - command arguments
        return x key
        """
        if args.dataset in ['NIPA', 'NIUnderlyingDetail', 'FixedAssets',
                            'Regional']:
            xk = 'TimePeriod'
        elif args.dataset in ['InputOutput']:
            xk = 'Year'
        elif args.dataset in ['GDPbyIndustry', 'UnderlyingGDPbyIndustry']:
            xk = 'Year'
        elif args.dataset in ['MNE']:
            xk = 'Year'
        elif args.dataset in ['IIP']:
            xk = 'Year'
        elif args.dataset in ['ITA', 'IntlServTrade', 'IntlServSTA']:
            xk = 'Year'
        else:
            return None
        return xk


    def ds2yk(self, args):
        """ds2dn(args)
        args - command arguments
        return y key
        """
        if args.dataset in ['NIPA', 'NIUnderlyingDetail', 'FixedAssets',
                            'Regional']:
            yk = 'DataValue'
        elif args.dataset in ['InputOutput']:
            yk = 'DataValue'
        elif args.dataset in ['GDPbyIndustry', 'UnderlyingGDPbyIndustry']:
            yk = 'DataValue'
        elif args.dataset in ['MNE']:
            yk = 'DataValue'
        elif args.dataset in ['IIP']:
            yk = 'DataValue'
        elif args.dataset in ['ITA', 'IntlServTrade', 'IntlServSTA']:
            yk = 'DataValue'
        else:
            return None
        return yk

    def ds2sk(self, args):
        """ds2dn(args)
        args - command arguments
        return qualifying name for dataset
        """
        if args.dataset in ['NIPA', 'NIUnderlyingDetail', 'FixedAssets']:
            sk = 'LineDescription'
        elif args.dataset in ['InputOutput']:
            sk = 'ColDescr'
        elif args.dataset in ['GDPbyIndustry', 'UnderlyingGDPbyIndustry']:
            sk = 'IndustrYDescription'
        elif args.dataset in ['MNE']:
            #sk = args.sid
            sk = 'SeriesName'
        elif args.dataset in ['IIP']:
            sk = 'Component'
        elif args.dataset in ['ITA', 'IntlServTrade', 'IntlServSTA']:
            sk = 'TimeSeriesDescription'
        elif args.dataset in ['Regional']:
            sk = 'GeoName'
        else:
            return None
        return sk


    def ds2dn(self, args):
        """ds2dn(args)
        args - command arguments
        return qualifying name for dataset
        """
        if args.dataset in ['NIPA', 'NIUnderlyingDetail', 'FixedAssets',
                            'Regional']:
            dn = args.tn
        elif args.dataset in ['InputOutput', 'GDPbyIndustry',
                              'UnderlyingGDPbyIndustry']:
            dn = args.tid
        elif args.dataset in ['MNE']:
            #dn = args.sid
            dn = args.doi
        elif args.dataset in ['IIP']:
            dn = args.toi
        elif args.dataset in ['ITA']:
            dn = args.indctr
        elif args.dataset in ['IntlServTrade']:
            dn = args.tos
        elif args.dataset in ['IntlServSTA']:
            dn = args.chan
        else:
            dn =  'Unkown'
        return dn

    def d2html(self, d, args):
        """d2html(d, ds, d, sk, xk, yk, uk)
        d - dictionary from table query
        fn - name of file to store html
        sk - split the data based on field name or None
        xk - key to x axis data
        yk - key to y axis data
        uk - key to y axis units
        """

        ds = args.dataset
        dn = self.ds2dn(args)
        sk = args.splitkey
        if sk == None:
            sk = self.ds2sk(args)
        xk = args.xkey
        if xk == None:
            xk = self.ds2xk(args)
        yk = args.ykey
        if yk == None:
            yk = self.ds2yk(args)
        uk = args.unitskey
        if uk == None:
            uk = self.ds2uk(args)

        htmla = []
        htmla.append('<html>')
        ttl = 'BEA Dataset %s Table %s' % (ds, dn)
        htmla.append('<head>')
        htmla.append('<title>%s</title>' % (ttl) )
        htmla.append('<script src="https://cdn.plot.ly/plotly-2.32.0.min.js" charset="utf-8"></script>')
        htmla.append('</head>')
        if type(d) == type({}):
            aa = self.dd2aa(d, 'Data')
            if sk != None:
                asp = self.aasplit(aa, sk)

                fig = self.paa2plots(asp['parts'], xk, yk, uk, '%s %s' %
                      (ds, dn))
                figjs = fig.to_json()
                htmla.append('<div id="fig%s%s">' % (ds,dn) )
                htmla.append('<script>')
                htmla.append('var figobj = %s;\n' % figjs)
                htmla.append('Plotly.newPlot("fig%s%s", figobj.data, figobj.layout, {});' % (ds,dn) )
                htmla.append('</script>')
                htmla.append('</div>')

                for pk in asp['parts'].keys():
                    pttl = '%s %s' % (ttl, pk)
                    ptbla = self.aa2table(pttl, asp['parts'][pk])
                    htmla.extend(ptbla)
            else:
                tbla = self.aa2table(ttl, aa)
                htmla.extend(tbla)
        elif type(d) == type([]):
            for i in range(len(d)):
                aa = self.dd2aa(d[i], 'Data')
                if sk != None:
                    asp = self.aasplit(aa, sk)

                    fig = self.paa2plots(asp['parts'], xk, yk, uk, '%s %s' %
                                         (ds, dn))
                    figjs = fig.to_json()
                    htmla.append('<div id="fig%s%s">' % (ds,dn) )
                    htmla.append('<script>')
                    htmla.append('var figobj = %s;\n' % figjs)
                    htmla.append('Plotly.newPlot("fig%s%s", figobj.data, figobj.layout, {});' % (ds,dn) )
                    htmla.append('</script>')
                    htmla.append('</div>')


                    for pk in asp['parts'].keys():
                        pttl = '%s %d %s' % (ttl, i, pk)
                        ptbla = self.aa2table(pttl, asp['parts'][pk])
                        htmla.extend(ptbla)
                else:
                    tbla = self.aa2table('%s %d' % (ttl, i), aa)
                    htmla.extend(tbla)
        htmla.append('</html>')
        return ''.join(htmla)


    def aa2csv(self, aa):
        """aa2csv(aa)
        aa - array of arrays
        return csv text rendition of aa
        """
        csva = []
        for a in aa:
            csva.append('"%s"' % '","'.join(a))
        return '\n'.join(csva)

    def dsparamvals(self, ds, param, fmt):
        """ dsparamvale(ds, param, fmt)
        ds - dataset name
        param - parameter name
        fmt - result format
        retrieve parameter values for BEA dataset parameter
        """
        params = ('&method=GetParameterValues&'
                  'Datasetname=%s&'
                  'ParameterName=%s&'
                  'ResultFormat=%s' % (ds, param, fmt))
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('dsparamvale: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        return rstr

    def dsparams(self, ds, fmt):
        """ dsparams(ds, fmt)
        ds - dataset name
        fmt - result format
        retrieve parameter list for a BEA dataset
        """
        params = ('&method=GetParameterList&'
                  'Datasetname=%s&'
                  'ResultFormat=%s' % (ds, fmt))
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('dsparams: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        return rstr

    def datasets(self, fmt):
        """ datasets(fmt)
        fmt - result format
        retrieve BEA datasets list
        """
        params = ('&method=GetDatasetList&'
                  'ResultFormat=%s' % fmt)
        url = self.burl + params
        resp = self.uq.query(url)
        if resp == None:
            print('datasets: no response', file=sys.stderr)
            return resp
        rstr = resp.read().decode('utf-8')
        return rstr

    def hierarchyhtml(self, hier):
        """ hierarchyhtml(hier)
        hier - dictionary of BEA data model
        return html page for BEA data model
        """
        htmla = []
        htmla.append('<html>')
        ttl = 'BEA Dataset Data Hierarchy'
        htmla.append('<head><h1>%s</h1></head>' % (ttl) )
        dsaa = hier['Datasets']
        tbl = self.aa2table('Datasets', dsaa)
        htmla.extend(tbl)
        for i in range(1, len(dsaa)):
            dsn = dsaa[i][0]
            paa = hier[dsn]['Parameter']
            tbl = self.aa2table('%s Parameters' % dsn, paa)
            htmla.extend(tbl)
            for j in range(1, len(paa)):
                pn = paa[j][0]
                pvaa = hier[dsn]['ParameterValue'][pn]
                tbl = self.aa2table('%s Parameter %s Values' % (dsn, pn), pvaa)
                htmla.extend(tbl)
        htmla.append('</html>')
        return ''.join(htmla)

    def showhtml(self, fn, html):
        with open(fn, 'w') as fp:
            fp.write(html)
        webbrowser.open('file://%s' % fn)

    def hierarchy(self, fmt):
        """ hierarchy(fmt)
        fmt - result format
        retrieve BEA data model
        """
        hier = {}
        dss = self.datasets(fmt)
        if fmt == 'json':
            dsaa = self.js2aa(dss, 'Dataset')
        else:
           dsaa = self.x2aa(dss, 'Dataset')
        hier['Datasets'] = dsaa
        for i in range(1, len(dsaa)):
            dsn = dsaa[i][0]
            hier[dsn] = {}
            pss = self.dsparams(dsn, fmt)
            if fmt == 'json':
                paa = self.js2aa(pss, 'Parameter')
            else:
                paa = self.x2aa(pss, 'Parameter')
            hier[dsn]['Parameter'] = paa
            hier[dsn]['ParameterValue'] = {}
            for j in range(1, len(paa)):
                pn = paa[j][0]
                psv = self.dsparamvals(dsn, pn, fmt)
                if fmt == 'json':
                    vaa = self.js2aa(psv, 'ParamValue')
                else:
                    vaa = self.x2aa(psv, 'ParamValue')
                hier[dsn]['ParameterValue'][pn] = vaa
        return hier

#
def main():
    argp = argparse.ArgumentParser(description='get BEA data')

    argp.add_argument('--dataset', choices=['NIPA', 'NIUnderlyingDetail', 'MNE',
                      'FixedAssets', 'ITA', 'IIP', 'InputOutput',
                      'IntlServTrade', 'IntlServSTA', 'GDPbyIndustry',
                      'Regional', 'UnderlyingGDPbyIndustry',
                      'APIDatasetMetaData'],
                      help='dataset name')

    argp.add_argument('--tn', help='NIPA NIUnderlyingDetail '
                                      'FixedAssets Regional table name')
    argp.add_argument('--tid', help='InputOutput GDPbyIndustry '
                                      'UnderlyingGDPbyIndustry table id')
    argp.add_argument('--sid', help='MNE series id')

    argp.add_argument('--showm', default='N',
                      help='NIPA show millions')
    argp.add_argument('--freq',
                     help='frequency M, Q, A or comma separated list')
    argp.add_argument('--yr',
                      help='year YYYY  X or all')

    argp.add_argument('--doi',
                      choices = ['inward', 'outward', 'parent', 'state'],
                      help='MNE direction of investment ')
    argp.add_argument('--cls', help='MNE classification')
    argp.add_argument('--indstry', help='MNE IntlServSTA GDPbyIndustry '
                                    'UnderlyingGDPbyIndustry Industry')
    argp.add_argument('--cnt', help='MNE country')

    argp.add_argument('--indctr', help='ITA indicator')
    argp.add_argument('--aoc', help='ITA IntlServTrade IntlServSTA '
                                    'area or country')

    argp.add_argument('--toi', help='IIP type of investment')
    argp.add_argument('--comp', help='IIP component')

    argp.add_argument('--tos', help='IntlServTrade type of service')
    argp.add_argument('--tdir', help='IntlServTrade trade direction')
    argp.add_argument('--affl', help='IntlServTrade affiliation')

    argp.add_argument('--chan', help='IntlServSTA channel')
    argp.add_argument('--dest', help='IntlServSTA destination')

    argp.add_argument('--fips', help='Regional geo FIPS')
    argp.add_argument('--lncd', help='Regional line code')

    argp.add_argument('--csvfn', \
         help='name of file to store dataset CSV result')

    argp.add_argument('--splitkey',
        help='table column name to use to split the table')
    argp.add_argument('--xkey',
        help='table column name to use to plot the data')
    argp.add_argument('--ykey', default='DataValue',
        help='table column name to use to plot the data')
    argp.add_argument('--unitskey',
        help='table column name to use to label the data')
    argp.add_argument('--htmlfn', \
        help='name of file to store dataset HTML result')

    argp.add_argument('--format', default='json',
                      choices=['json', 'XML'], help='query result format')

    argp.add_argument('--hierarchy',
                      action='store_true', default=False,
                      help='BEA data model ')
    argp.add_argument('--tableregister',
                      action='store_true', default=False,
                      help='get NIPA table register ')

    args=argp.parse_args()

    BN = BEAQueryQ()
    BN.args = args

    if args.tableregister:
       txt = BN.getNIPAregister()
       print(txt)
    elif args.tn:
        d = None
        if args.dataset == None:
            print('dataset required to print dataset tables')
            argp.print_help()
            sys.exit()
        if args.dataset == 'NIPA':
            if args.freq == None or args.yr == None:
                argp.print_help()
                sys.exit()
            d = BN.getNIPAdata(args)
        elif args.dataset == 'NIUnderlyingDetail':
            d = BN.getNIUnderlyingDetaildata(args)
        elif args.dataset == 'FixedAssets':
            d = BN.getFixedAssetsdata(args)
        elif args.dataset == 'Regional':
            d = BN.getRegionaldata(args)
        else:
            argp.print_help()
            sys.exit()
        if d == None:
            print('beaqueryq: no data', file=sys.stderr)
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
    elif args.tid:
        d = None
        if args.dataset =='InputOutput':
            d = BN.getInputOutputdata(args)
        elif args.dataset == 'GDPbyIndustry':
            d = BN.getGDPbyIndustrydata(args)
        elif args.dataset == 'UnderlyingGDPbyIndustry':
            d = BN.getUnderlyingGDPbyIndustrydata(args)
        else:
            argp.print_help()
            sys.exit()
        if d == None:
            print('beaqueryq: no data', file=sys.stderr)
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
    elif args.sid:
        d = None
        if args.dataset == 'MNE':
            d = BN.getMNEdata(args)
        else:
            argp.print_help()
            sys.exit()
        if d == None:
            print('beaqueryq: no data', file=sys.stderr)
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
    elif args.toi:
        d = None
        if args.dataset == 'IIP':
            d = BN.getIIPdata(args)
        else:
            argp.print_help()
            sys.exit()
        if d == None:
            print('beaqueryq: no data', file=sys.stderr)
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
    elif args.indctr:
        d = None
        if args.dataset == 'ITA':
            d = BN.getITAdata(args)
        else:
            argp.print_help()
            sys.exit()
        if d == None:
            print('beaqueryq: no data', file=sys.stderr)
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
    elif args.tos:
        d = None
        if args.dataset == 'IntlServTrade':
            d = BN.getIntlServTradedata(args)
        else:
            argp.print_help()
            sys.exit()
        if d == None:
            print('beaqueryq: no data', file=sys.stderr)
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
    elif args.chan:
        d = None
        if args.dataset == 'IntlServSTA':
            d = BN.getIntlServSTAdata(args)
        else:
            argp.print_help()
            sys.exit()
        if d == None:
            print('beaqueryq: no data', file=sys.stderr)
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
    elif args.hierarchy:
        hd = BN.hierarchy(args.format)
        htm = BN.hierarchyhtml(hd)
        BN.showhtml('/tmp/hierarchy.html', htm)
    else:
        argp.print_help()
        sys.exit()


if __name__ == '__main__':
    main()
