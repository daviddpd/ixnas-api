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


def requestCheck(args, response):
    pp = pprint.PrettyPrinter(indent=4)

    if args.verbose or  response.status_code < 200 or response.status_code > 299:
        print response
        try:
            pp.pprint( response.json() );
        except:
            if ( response.status_code != 204 ):
                print " Error, Response body is empty and HTTP code is %s " % response.status_code
                raise
            else:
                print "Expected Response: HTTP %s, no response body content." % response.status_code

        if response.status_code < 200 or response.status_code > 299:
            sys.exit(1)
