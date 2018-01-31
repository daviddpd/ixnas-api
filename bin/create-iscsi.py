#!/usr/local/bin/python2.7
import argparse
import requests
import pprint
import json
import ConfigParser
import re
import os.path
import uuid
import sys

_uuid = uuid.uuid1()
pp = pprint.PrettyPrinter(indent=4)


parser = argparse.ArgumentParser(description='Create/Map a ZVOL on a TrueNAS or FreeNAS Appliance to an iSCSI target/lun.')

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


_ds = "%x-%x-%02d" % ( _uuid.fields[0], _uuid.fields[1], 0 )
parser.add_argument('--diskserial',
        required=False,
        type=str,
        nargs=1,
        default=[ _ds ],
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

parser.add_argument('--blocksize',
        required=False,
        default=[ 512 ],
        type=int,
        nargs=1,
        help='Extent Logical Block Size'
        )

parser.add_argument('--compression',
        required=False,
        type=str,
        default=['off'],
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

parser.add_argument('--verbose',
        required=False,
        action='store_true',
        help='Verbose Output/debugging'
        )


args = parser.parse_args()

if args.verbose:
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

try:
    iscsi_target_authgroup=config.get(args.host[0], "iscsi_target_authgroup");
except:
    iscsi_target_authgroup=''

try:
    iscsi_target_authtype=config.get(args.host[0], "iscsi_target_authtype");
except:
    iscsi_target_authtype=''

try:
    iscsi_target_portalgroup=config.get(args.host[0], "iscsi_target_portalgroup");
except:
    iscsi_target_portalgroup=''

try:
    iscsi_target_initiatorgroup=config.get(args.host[0], "iscsi_target_initiatorgroup");
except:
    iscsi_target_initiatorgroup=''

try:    
    iscsi_target_initialdigest=config.get(args.host[0], "iscsi_target_initialdigest");
except:
    iscsi_target_initialdigest=''

if len(bp):
    match = re.search("^" + bp + "/", args.name[0])
    if match:
        volname = args.name[0]
        targetname = re.sub("^" + bp + "/", '', args.name[0]);
    else:
        volname = bp + "/" + args.name[0]
        targetname = args.name[0]
else:
    volname = args.name[0]

try:
    args.zpool[0]
    zpool = args.zpool[0]
except:
    zpool = config.get(args.host[0], "zpool");
    
try:
    args.blocksize[0]
    blocksize = args.blocksize[0]
except:
    blocksize = 512


targetdata=json.dumps({
  "iscsi_target_name": targetname,
  "iscsi_target_name": targetname,
})

if args.verbose:
    print targetdata

target = requests.post(
    "http://%s//api/v1.0/services/iscsi/target/" % (args.host[0]),
    auth=(u, p),
    headers={'Content-Type': 'application/json'},
    verify=False,
    data=targetdata,
)

if args.verbose or target.status_code < 200 or target.status_code > 299:
    print targetdata
    print target
    pp.pprint( target.json() );
    if target.status_code < 200 or target.status_code > 299:
        sys.exit(1)

t = target.json();





#POST /api/v1.0/services/iscsi/targetgroup/ HTTP/1.1
#Content-Type: application/json

targetgroup_data = json.dumps({
  "iscsi_target": t['id'],
  "iscsi_target_portalgroup": iscsi_target_portalgroup,
  "iscsi_target_initiatorgroup": iscsi_target_initiatorgroup, 
})

targetgroup = requests.post(
    "http://%s//api/v1.0/services/iscsi/targetgroup/" % (args.host[0]),
    auth=(u, p),
    headers={'Content-Type': 'application/json'},
    verify=False,
    data=targetgroup_data,
)

if args.verbose or  targetgroup.status_code < 200 or targetgroup.status_code > 299:
    print targetgroup
    pp.pprint( targetgroup.json() );
    if targetgroup.status_code < 200 or targetgroup.status_code > 299:
        sys.exit(1)

extentdata=json.dumps({
  "iscsi_target_extent_type": "Disk",
  "iscsi_target_extent_blocksize": blocksize,
  "iscsi_target_extent_name": targetname,
  "iscsi_target_extent_disk": "zvol/" + zpool + "/" + volname,
  "iscsi_target_extent_serial": args.diskserial[0],
})

ext = requests.post(
    "http://%s//api/v1.0/services/iscsi/extent/" % (args.host[0]),
    auth=(u, p),
    headers={'Content-Type': 'application/json'},
    verify=False,
    data=extentdata,
)

if args.verbose or ext.status_code < 200 or ext.status_code > 299:
    print ext
    pp.pprint( ext.json() );
    if ext.status_code < 200 or ext.status_code > 299:
        sys.exit(1)

e = ext.json();

e2t=json.dumps({
  "iscsi_target": t['id'],
  "iscsi_extent": e['id'],
})

if args.verbose:
    print e2t
    
ext = requests.post(
    "http://%s//api/v1.0/services/iscsi/targettoextent/" % (args.host[0]),
    auth=(u, p),
    headers={'Content-Type': 'application/json'},
    verify=False,
    data=e2t,
)

if args.verbose or ext.status_code < 200 or ext.status_code > 299:
    print ext
    pp.pprint( ext.json() );
    if ext.status_code < 200 or ext.status_code > 299:
        sys.exit(1)


sys.exit(0)
