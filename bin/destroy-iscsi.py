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
import urllib3
urllib3.disable_warnings()

sys.path.append(os.path.abspath("/home/dpd/ixnas-api/bin"))

from requestCheck import requestCheck

_uuid = uuid.uuid1()
pp = pprint.PrettyPrinter(indent=4)


parser = argparse.ArgumentParser(description='Destroy/unMap a ZVOL on a TrueNAS or FreeNAS Appliance to an iSCSI target/lun.')

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
        required=False,
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


ext2target = requests.get(
    "https://%s//api/v1.0/services/iscsi/targettoextent/" % (args.host[0]),
    auth=(u, p),
    headers={'Content-Type': 'application/json'},
    verify=False,
)
if args.verbose:
    pp.pprint(ext2target)

requestCheck(args, ext2target)

ext = requests.get(
    "https://%s//api/v1.0/services/iscsi/extent/" % (args.host[0]),
    auth=(u, p),
    headers={'Content-Type': 'application/json'},
    verify=False,
)

requestCheck(args, ext)

targetgroup = requests.get(
    "https://%s//api/v1.0/services/iscsi/targetgroup/" % (args.host[0]),
    auth=(u, p),
    headers={'Content-Type': 'application/json'},
    verify=False,
)

requestCheck(args, targetgroup)

target = requests.get(
    "https://%s//api/v1.0/services/iscsi/target/" % (args.host[0]),
    auth=(u, p),
    headers={'Content-Type': 'application/json'},
    verify=False,
)

requestCheck(args, target)

_targets_byid = {}
_targets_byname = {}
_extents_byid = {}

for i in target.json():    
    try:
        id = i['id']
        name = i['iscsi_target_name']
        _targets_byid[id] = i
        _targets_byname[name] = i
    except:
        pp.pprint (i)

for i in targetgroup.json():
    tid = i['iscsi_target']
    tname = _targets_byid[tid]['iscsi_target_name']
    _targets_byid[tid]['targetgroup'] = i
    _targets_byname[tname]['targetgroup'] = i


for i in ext.json():
    eid = i['id']
    _extents_byid[eid] = i    

for i in ext2target.json():
    tid = i['iscsi_target']
    eid = i['iscsi_extent']
    tname = _targets_byid[tid]['iscsi_target_name']

    _targets_byid[tid]['targettoextent'] = i
    _targets_byname[tname]['targettoextent'] = i

    _targets_byid[tid]['extent'] = _extents_byid[eid]
    _targets_byname[tname]['extent'] = _extents_byid[eid]
    
    
if args.verbose:
    pp.pprint ( _targets_byname ) 
    
name = args.name[0]
    
try:
    _targettoextent_id = _targets_byname[name]['targettoextent']['id']

    ext2target = requests.delete(
        "https://%s//api/v1.0/services/iscsi/targettoextent/%d" % (args.host[0], _targettoextent_id),
        auth=(u, p),
        headers={'Content-Type': 'application/json'},
        verify=False,
    )
    requestCheck(args, ext2target)
except:
    print "Allowable error:", sys.exc_info()[0]
    print sys.exc_info()
    

try:
    _extent_id = _targets_byname[name]['extent']['id']
    
    ext = requests.delete(
        "https://%s//api/v1.0/services/iscsi/extent/%d" % (args.host[0], _extent_id),
        auth=(u, p),
        headers={'Content-Type': 'application/json'},
        verify=False,
    )
    requestCheck(args, ext)
except:
    print "Allowable error:", sys.exc_info()[0]
    print sys.exc_info()

try:
    _targetgroup_id = _targets_byname[name]['targetgroup']['id']
    targetgroup = requests.delete(
        "https://%s//api/v1.0/services/iscsi/targetgroup/%d" % (args.host[0], _targetgroup_id),
        auth=(u, p),
        headers={'Content-Type': 'application/json'},
        verify=False,
    )
    requestCheck(args, targetgroup)
except:
    print "Allowable error:", sys.exc_info()[0]
    print sys.exc_info()
    
        
  
try:
    _target_id = _targets_byname[name]['id']
    target = requests.delete(
        "https://%s//api/v1.0/services/iscsi/target/%d" % (args.host[0], _target_id),
        auth=(u, p),
        headers={'Content-Type': 'application/json'},
        verify=False,
    )

    requestCheck(args, target)
except:
    print "Allowable error:", sys.exc_info()[0]
    
    
        
# 
# 
# 
# targetdata=json.dumps({
#   "iscsi_target_name": targetname,
#   "iscsi_target_name": targetname,
# })
# 
# if args.verbose:
#     print targetdata
# 
# target = requests.post(
#     "https://%s//api/v1.0/services/iscsi/target/" % (args.host[0]),
#     auth=(u, p),
#     headers={'Content-Type': 'application/json'},
#     verify=False,
#     data=targetdata,
# )
# 
# if args.verbose or target.status_code < 200 or target.status_code > 299:
#     print targetdata
#     print target
#     pp.pprint( target.json() );
#     if target.status_code < 200 or target.status_code > 299:
#         sys.exit(1)
# 
# t = target.json();
# 
# 
# 
# 
# 
# #POST /api/v1.0/services/iscsi/targetgroup/ https/1.1
# #Content-Type: application/json
# 
# targetgroup_data = json.dumps({
#   "iscsi_target": t['id'],
#   "iscsi_target_portalgroup": iscsi_target_portalgroup,
#   "iscsi_target_initiatorgroup": iscsi_target_initiatorgroup, 
# })
# 
# targetgroup = requests.post(
#     "https://%s//api/v1.0/services/iscsi/targetgroup/" % (args.host[0]),
#     auth=(u, p),
#     headers={'Content-Type': 'application/json'},
#     verify=False,
#     data=targetgroup_data,
# )
# 
# if args.verbose or  targetgroup.status_code < 200 or targetgroup.status_code > 299:
#     print targetgroup
#     pp.pprint( targetgroup.json() );
#     if targetgroup.status_code < 200 or targetgroup.status_code > 299:
#         sys.exit(1)
# 
# extentdata=json.dumps({
#   "iscsi_target_extent_type": "Disk",
#   "iscsi_target_extent_blocksize": blocksize,
#   "iscsi_target_extent_name": targetname,
#   "iscsi_target_extent_disk": "zvol/" + zpool + "/" + volname,
#   "iscsi_target_extent_serial": args.diskserial[0],
# })
# 
# ext = requests.post(
#     "https://%s//api/v1.0/services/iscsi/extent/" % (args.host[0]),
#     auth=(u, p),
#     headers={'Content-Type': 'application/json'},
#     verify=False,
#     data=extentdata,
# )
# 
# if args.verbose or ext.status_code < 200 or ext.status_code > 299:
#     print ext
#     pp.pprint( ext.json() );
#     if ext.status_code < 200 or ext.status_code > 299:
#         sys.exit(1)
# 
# e = ext.json();
# 
# e2t=json.dumps({
#   "iscsi_target": t['id'],
#   "iscsi_extent": e['id'],
# })
# 
# if args.verbose:
#     print e2t
#     
# 
# 
# sys.exit(0)
