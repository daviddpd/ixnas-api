#!/usr/local/bin/python2.7
import argparse
import requests
import pprint
import json
import ConfigParser
import re
import os.path

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

parser.add_argument('--diskserial',
        required=True,
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

parser.add_argument('--blocksize',
        required=False,
        type=str,
        nargs=1,
        help='zvol size'
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
    print match
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
    zpool = args.blocksize[0]
except:
    blocksize = config.get(args.host[0], "blocksize");


targetdata=json.dumps({
  "iscsi_target_name": targetname,
  "iscsi_target_name": targetname,
})

print targetdata



target = requests.post(
    "http://%s//api/v1.0/services/iscsi/target/" % (args.host[0]),
    auth=(u, p),
    headers={'Content-Type': 'application/json'},
    verify=False,
    data=targetdata,
)

print target
t = target.json();

pp.pprint( target.json() );




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

print targetgroup
pp.pprint( targetgroup.json() );

extentdata=json.dumps({
  "iscsi_target_extent_type": "Disk",
  "iscsi_target_extent_blocksize": 4096,
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

print ext

pp.pprint( ext.json() );

e = ext.json();

e2t=json.dumps({
  "iscsi_target": t['id'],
  "iscsi_extent": e['id'],
})

print e2t
ext = requests.post(
    "http://%s//api/v1.0/services/iscsi/targettoextent/" % (args.host[0]),
    auth=(u, p),
    headers={'Content-Type': 'application/json'},
    verify=False,
    data=e2t,
)

print ext

pp.pprint( ext.json() );

