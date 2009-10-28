#! /usr/bin/env python
from __future__ import with_statement

import sys
import os, os.path
import tempfile
import xmlrpclib
from types import StringTypes, ListType
from optparse import OptionParser

from sfa.trust.certificate import Certificate
from sfa.trust.credential import Credential

from sfa.util.geniclient import GeniClient
from sfa.util.record import GeniRecord
from sfa.util.rspec import Rspec

def determine_sfa_filekind(fn):
    cert = Certificate(filename = fn)

    data = cert.get_data()
    if data:
        dict = xmlrpclib.loads(data)[0][0]
    else:
        dict = {}

    if "gidCaller" in dict:
        return "credential"

    if "uuid" in dict:
        return "gid"

    return "unknown"

def save_gid(gid):
   hrn = gid.get_hrn()
   lastpart = hrn.split(".")[-1]
   filename = lastpart + ".gid"

   if os.path.exists(filename):
       print filename, ": already exists... skipping"
       return

   print filename, ": extracting gid of", hrn

   gid.save_to_file(filename, save_parents = True)

def extract_gids(cred, extract_parents):
   gidCaller = cred.get_gid_caller()
   if gidCaller:
       save_gid(gidCaller)

   gidObject = cred.get_gid_object()
   if gidObject and ((gidCaller == None) or (gidCaller.get_hrn() != gidObject.get_hrn())):
       save_gid(gidObject)

   if extract_parents:
       parent = cred.get_parent()
       if parent:
           extract_gids(parent, extract_parents)

def create_parser():
   # Generate command line parser
   parser = OptionParser(usage="genidump [options] filename")

   parser.add_option("-e", "--extractgids", action="store_true", dest="extract_gids", default=False, help="Extract GIDs from credentials")
   parser.add_option("-p", "--dumpparents", action="store_true", dest="dump_parents", default=False, help="Show parents")

   return parser

def main():
   parser = create_parser()
   (options, args) = parser.parse_args()

   if len(args) <= 0:
        print "No filename given. Use -h for help."
        return -1

   filename = args[0]
   kind = determine_sfa_filekind(filename)

   if kind=="credential":
       cred = Credential(filename = filename)
       cred.dump(dump_parents = options.dump_parents)
       if options.extract_gids:
           extract_gids(cred, extract_parents = options.dump_parents)
   elif kind=="gid":
       gid = Gid(filename = filename)
       gid.dump(dump_parents = options.dump_parents)
   else:
       print "unknown filekind", kind

if __name__=="__main__":
   main()
