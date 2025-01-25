# BEAquery

[![PyPI - Version](https://img.shields.io/pypi/v/beaquery.svg)](https://pypi.org/project/beaquery)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/beaquery.svg)](https://pypi.org/project/beaquery)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation
<br>
```console<br>
pip&nbsp;install&nbsp;beaquery<br>
```<br>
<br>
##&nbsp;License<br>
<br>
`beaquery`&nbsp;is&nbsp;distributed&nbsp;under&nbsp;the&nbsp;terms&nbsp;of&nbsp;the&nbsp;[MIT](https://spdx.org/licenses/MIT.html)&nbsp;license.<br>
<br>
<p><br>
<br/>

<br/>
##<br/>
## beafixedassets<br/>
##<br/>
usage: beafixedassets [-h] --tn TN --yr YR [--format {json,XML}]<br/>
<br/>
get BEA fixed assets data<br/>
<br/>
options:<br/>
-h, --help           show this help message and exit<br/>
--tn TN              FixedAssets table name<br/>
--yr YR              year YYYY X or all<br/>
--format {json,XML}  result format<br/>
<br/>
<br/>
##<br/>
## beagdpbyind<br/>
##<br/>
usage: beagdpbyind [-h] --tid TID --indstry INDSTRY --freq FREQ --yr YR<br/>
[--format {json,XML}]<br/>
<br/>
get BEA GDP by industry data<br/>
<br/>
options:<br/>
-h, --help           show this help message and exit<br/>
--tid TID            table id<br/>
--indstry INDSTRY    industry<br/>
--freq FREQ          frequency M, Q, A or comma separated list<br/>
--yr YR              year YYYY X or all<br/>
--format {json,XML}  result format<br/>
<br/>
<br/>
##<br/>
## beaiip<br/>
##<br/>
usage: beaiip [-h] --toi TOI --comp COMP --freq FREQ --yr YR<br/>
[--format {json,XML}]<br/>
<br/>
get BEA IIP data<br/>
<br/>
options:<br/>
-h, --help           show this help message and exit<br/>
--toi TOI            type of investment<br/>
--comp COMP          composition<br/>
--freq FREQ          frequency M, Q, A or comma separated list<br/>
--yr YR              year YYYY X or all<br/>
--format {json,XML}  result format<br/>
<br/>
<br/>
##<br/>
## beainputoutput<br/>
##<br/>
usage: beainputoutput [-h] --tid TID --yr YR [--format {json,XML}]<br/>
<br/>
get BEA InputOutput data<br/>
<br/>
options:<br/>
-h, --help           show this help message and exit<br/>
--tid TID            table id<br/>
--yr YR              year YYYY X or all<br/>
--format {json,XML}  result format<br/>
<br/>
<br/>
##<br/>
## beaissta<br/>
##<br/>
usage: beaissta [-h] --chan CHAN --dest DEST --indstry INDSTRY --aoc AOC<br/>
--yr YR [--format {json,XML}]<br/>
<br/>
get BEA IntlServSTA data<br/>
<br/>
options:<br/>
-h, --help           show this help message and exit<br/>
--chan CHAN          channel<br/>
--dest DEST          destination<br/>
--indstry INDSTRY    industry<br/>
--aoc AOC            area or country<br/>
--yr YR              year YYYY X or all<br/>
--format {json,XML}  result format<br/>
<br/>
<br/>
##<br/>
## beaistrade<br/>
##<br/>
usage: beaistrade [-h] --tos TOS [--tdir TDIR] [--affl AFFL] [--aoc AOC]<br/>
--yr YR [--format {json,XML}]<br/>
<br/>
get BEA IntlServTrade data<br/>
<br/>
options:<br/>
-h, --help           show this help message and exit<br/>
--tos TOS            type of service<br/>
--tdir TDIR          trade direction<br/>
--affl AFFL          affiliation<br/>
--aoc AOC            area or country<br/>
--yr YR              year YYYY X or all<br/>
--format {json,XML}  result format<br/>
<br/>
<br/>
##<br/>
## beaita<br/>
##<br/>
usage: beaita [-h] --indctr INDCTR --aoc AOC --freq FREQ --yr YR<br/>
[--format {json,XML}]<br/>
<br/>
get BEA ITA data<br/>
<br/>
options:<br/>
-h, --help           show this help message and exit<br/>
--indctr INDCTR      ITA indicator<br/>
--aoc AOC            ITA area or country<br/>
--freq FREQ          frequency M, Q, A or comma separated list<br/>
--yr YR              year YYYY X or all<br/>
--format {json,XML}  result format<br/>
<br/>
<br/>
##<br/>
## beamne<br/>
##<br/>
usage: beamne [-h] --sid SID [--doi DOI] [--cls CLS] [--cnt CNT]<br/>
[--indstry INDSTRY] --yr YR [--format {json,XML}]<br/>
<br/>
get BEA MNE data<br/>
<br/>
options:<br/>
-h, --help           show this help message and exit<br/>
--sid SID            MNE series id<br/>
--doi DOI            direction of investment<br/>
--cls CLS            classification<br/>
--cnt CNT            country<br/>
--indstry INDSTRY    industry<br/>
--yr YR              year YYYY X or all<br/>
--format {json,XML}  result format<br/>
<br/>
<br/>
##<br/>
## beanipa<br/>
##<br/>
usage: beanipa [-h] --tn TN [--showm SHOWM] --freq FREQ --yr YR<br/>
[--format {json,XML}]<br/>
<br/>
get BEA NIPA data<br/>
<br/>
options:<br/>
-h, --help           show this help message and exit<br/>
--tn TN              NIPA table name<br/>
--showm SHOWM        NIPA show millions<br/>
--freq FREQ          frequency M, Q, A or comma separated list<br/>
--yr YR              year YYYY X or all<br/>
--format {json,XML}  result format<br/>
<br/>
<br/>
##<br/>
## beaniud<br/>
##<br/>
usage: beaniud [-h] --tn TN --freq FREQ --yr YR [--format {json,XML}]<br/>
<br/>
get BEA NI underlyingdetail data<br/>
<br/>
options:<br/>
-h, --help           show this help message and exit<br/>
--tn TN              NIUnderlyingDetail table name<br/>
--freq FREQ          frequency M, Q, A or comma separated list<br/>
--yr YR              year YYYY X or all<br/>
--format {json,XML}  result format<br/>
<br/>
<br/>
##<br/>
## bearegional<br/>
##<br/>
usage: bearegional [-h] --tn TN --fips FIPS --lncd LNCD --yr YR<br/>
[--format {json,XML}]<br/>
<br/>
get BEA Regional data<br/>
<br/>
options:<br/>
-h, --help           show this help message and exit<br/>
--tn TN              table name<br/>
--fips FIPS          geo fips<br/>
--lncd LNCD          line code<br/>
--yr YR              year YYYY X or all<br/>
--format {json,XML}  result format<br/>
<br/>
<br/>
##<br/>
## beaugdpbyind<br/>
##<br/>
usage: beaugdpbyind [-h] --tid TID --indstry INDSTRY --freq FREQ --yr YR<br/>
[--format {json,XML}]<br/>
<br/>
get BEA UnderlyingGDPbyIndustry data<br/>
<br/>
options:<br/>
-h, --help           show this help message and exit<br/>
--tid TID            table id<br/>
--indstry INDSTRY    industry<br/>
--freq FREQ          frequency M, Q, A or comma separated list<br/>
--yr YR              year YYYY X or all<br/>
--format {json,XML}  result format<br/>
<br/>
<br/>
##<br/>
## beaqueryq<br/>
##<br/>
usage: beaqueryq [-h]<br/>
[--dataset {NIPA,NIUnderlyingDetail,MNE,FixedAssets,ITA,IIP,InputOutput,IntlServTrade,IntlServSTA,GDPbyIndustry,Regional,UnderlyingGDPbyIndustry,APIDatasetMetaData}]<br/>
[--tn TN] [--tid TID] [--sid SID] [--showm SHOWM]<br/>
[--freq FREQ] [--yr YR]<br/>
[--doi {inward,outward,parent,state}] [--cls CLS]<br/>
[--indstry INDSTRY] [--cnt CNT] [--indctr INDCTR]<br/>
[--aoc AOC] [--toi TOI] [--comp COMP] [--tos TOS]<br/>
[--tdir TDIR] [--affl AFFL] [--chan CHAN] [--dest DEST]<br/>
[--fips FIPS] [--lncd LNCD] [--format {json,XML}]<br/>
[--hierarchy] [--tableregister]<br/>
<br/>
get BEA data<br/>
<br/>
options:<br/>
-h, --help            show this help message and exit<br/>
--dataset {NIPA,NIUnderlyingDetail,MNE,FixedAssets,ITA,IIP,InputOutput,IntlServTrade,IntlServSTA,GDPbyIndustry,Regional,UnderlyingGDPbyIndustry,APIDatasetMetaData}<br/>
dataset name<br/>
--tn TN               NIPA NIUnderlyingDetail FixedAssets Regional table<br/>
name<br/>
--tid TID             InputOutput GDPbyIndustry UnderlyingGDPbyIndustry<br/>
table id<br/>
--sid SID             MNE series id<br/>
--showm SHOWM         NIPA show millions<br/>
--freq FREQ           frequency M, Q, A or comma separated list<br/>
--yr YR               year YYYY X or all<br/>
--doi {inward,outward,parent,state}<br/>
MNE direction of investment<br/>
--cls CLS             MNE classification<br/>
--indstry INDSTRY     MNE IntlServSTA GDPbyIndustry UnderlyingGDPbyIndustry<br/>
Industry<br/>
--cnt CNT             MNE country<br/>
--indctr INDCTR       ITA indicator<br/>
--aoc AOC             ITA IntlServTrade IntlServSTA area or country<br/>
--toi TOI             IIP type of investment<br/>
--comp COMP           IIP component<br/>
--tos TOS             IntlServTrade type of service<br/>
--tdir TDIR           IntlServTrade trade direction<br/>
--affl AFFL           IntlServTrade affiliation<br/>
--chan CHAN           IntlServSTA channel<br/>
--dest DEST           IntlServSTA destination<br/>
--fips FIPS           Regional geo FIPS<br/>
--lncd LNCD           Regional line code<br/>
--format {json,XML}   result format<br/>
--hierarchy           BEA data model<br/>
--tableregister       get NIPA table register<br/>
<br/>
