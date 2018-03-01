#!/usr/local/bin/python2.7
import argparse
import requests
import pprint
import json
import ConfigParser
import re
import os.path
import sys
import urllib3
urllib3.disable_warnings()

pp = pprint.PrettyPrinter(indent=4)


parser = argparse.ArgumentParser(description='Create a ZVOL on a TrueNAS or FreeNAS Appliance')
parser.add_argument('--host',
        required=True,
        type=str,
        nargs=1,
        help='NAS Host name or IP'
        )

parser.add_argument('--vmname',
        required=True,
        type=str,
        nargs=1,
        help='Bhyve vm name'
        )

parser.add_argument('--name',
        required=True,
        type=str,
        nargs=1,
        help='zvol name'
        )


parser.add_argument('--zpool',
        required=False,
        type=str,
        nargs=1,
        help='zpool name'
        )

parser.add_argument('--verbose',
        required=False,
        action='store_true',
        help='Verbose Output/debugging'
        )

args = parser.parse_args()

if args.verbose:
    pp.pprint( args );

config = ConfigParser.RawConfigParser()

configfiles = [ "./ixnas-api.ini", "./config/ixnas-api.ini", "/usr/local/etc/ixnas-api.ini" ]
cnf = False
for f in configfiles:
    if os.path.isfile(f):
        cnf  = f
        break

    
config.read(cnf)
u = config.get(args.host[0], "user");
p = config.get(args.host[0], "password");
bp = config.get(args.host[0], "basepath");

if len(bp):
    match = re.search("^" + bp + "/", args.name[0])
    if match:
        volname = args.name[0]
    else:
        volname = bp + "/" + args.name[0]
else:
    volname = args.name[0]

try:
    args.zpool[0]
    zpool = args.zpool[0]
except:
    zpool = config.get(args.host[0], "zpool");
    
try:
    uuid = " / %s " % args.uuid[0]
except:
    uuid = '';


url = "https://%s/api/v1.0/storage/volume/%s/zvols/%s" % (args.host[0], zpool, volname )

if args.verbose:
    print " ==> zpool : " + zpool
    print " ==> url : " + url

zvols = requests.get(
    url,
    auth=(u, p),
    headers={'Content-Type': 'application/json'},
    verify=False,
)

if args.verbose:
    print " get id : " 
    pp.pprint( zvols.json() );

zvols = requests.delete(
    url,
    auth=(u, p),
    headers={'Content-Type': 'application/json'},
    verify=False,
)
if args.verbose or zvols.status_code < 200 or zvols.status_code > 299:
    print zvols
    if zvols.status_code < 200 or zvols.status_code > 299:
        sys.exit(1)

sys.exit(0)


