#!/usr/local/bin/python2.7
import argparse
import requests
import pprint
import json
import ConfigParser
import re
import os.path

pp = pprint.PrettyPrinter(indent=4)


parser = argparse.ArgumentParser(description='Create a ZVOL on a TrueNAS or FreeNAS Appliance')
parser.add_argument('--host',
        required=True,
        type=str,
        nargs=1,
        help='NAS Host name or IP'
        )

parser.add_argument('--uuid',
        required=False,
        type=str,
        nargs=1,
        help='Bhyve UUID'
        )

parser.add_argument('--diskserial',
        required=False,
        type=str,
        nargs=1,
        help='Bhyve Disk Serial Number'
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

parser.add_argument('--size',
        required=True,
        type=str,
        nargs=1,
        help='zvol size'
        )
parser.add_argument('--blocksize',
        required=False,
        type=str,
        nargs=1,
        help='zvol size'
        )

parser.add_argument('--compression',
        required=False,
        type=str,
        default=['lz4'],
        nargs=1,
        help='Compression'
        )

parser.add_argument('--zpool',
        required=False,
        type=str,
        nargs=1,
        help='zpool name'
        )

parser.add_argument('--sparse',
        required=False,
        action='store_true',
        help='Make as sparse volume'
        )


args = parser.parse_args()

pp.pprint( args );

config = ConfigParser.RawConfigParser()

configfiles = [ "./ixnas-api.ini", "./config/ixnas-api.ini", "/usr/local/etc/ixnas-api/config/ixnas-api.ini" ]
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
    print match
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
    args.blocksize[0]
    zpool = args.blocksize[0]
except:
    blocksize = config.get(args.host[0], "blocksize");

try:
    uuid = " / %s " % args.uuid[0]
except:
    uuid = '';


data=json.dumps({
  "comments": "iSCSI Bhyve zvol for %s %s" %  ( args.vmname[0], uuid ),
  "name": volname,
  "volsize": args.size[0],
  "compression": args.compression[0],
  "sparse": args.sparse,
  "force": True,
  "blocksize": blocksize,
  
});

print " ==> zpool : " + zpool
pp.pprint( data );

zvols = requests.post(
    "http://%s/api/v1.0/storage/volume/%s/zvols/" % (args.host[0], zpool ),
    auth=(u, p),
    headers={'Content-Type': 'application/json'},
    verify=False,
    data=data,
)

print zvols


pp.pprint( zvols.json() );

