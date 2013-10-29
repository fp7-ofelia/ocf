#!/usr/bin/env python
# Copyright 2012  Barnstormer Softworks

from sqlalchemy import (Table, Column, MetaData, Integer, String, Boolean,
                        PickleType, Text, create_engine, select)
from sqlalchemy.orm import scoped_session, sessionmaker

import urllib2
import json
import getpass
import pprint
import sys
import os.path
import time

DB_ENGINE = "sqlite:////tmp/foam.db"
CONFIGURL = "https://localhost:3626/core/admin/set-config"
IMPORTURL = "https://localhost:3626/core/admin/import-sliver"

if not os.path.exists("/tmp/foam.db"):
  print "You must copy your old foam.db file into /tmp/ before running this script"
  sys.exit(1)

engine = create_engine(DB_ENGINE)
metadata = MetaData(bind=engine)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False))

### Stub classes to satisfy pickle
class foam (object):
  class lib (object):
    class Sliver (object):
      def __init__ (self): pass
    class Controller (object):
      def __init__ (self): pass
    class FlowSpec (object):
      def __init__ (self): pass
    class Datapath (object):
      def __init__ (self): pass
  class flowvisor (object):
    class Port (object):
      def __init__ (self): pass
  

sys.modules["foam.lib"] = foam.lib
sys.modules["foam.flowvisor"] = foam.flowvisor

### Relevant old DB schema
t_config = Table('config', metadata,
  Column('key', String(256)),
  Column('value', PickleType))

t_slivers = Table('slivers', metadata,
    Column('id', Integer, primary_key=True),
    Column('slice_urn', String(256)),
    Column('sliver_urn', String(256)),
    Column('fvslicename', String(500)),
    Column('req_rspec', Text),
    Column('manifest_rspec', Text),
    Column('parsed_obj', PickleType),
    Column('expiration', PickleType),
    Column('priority', Integer),
    Column('status', Boolean, default=None),
    Column('deleted', Boolean, default=False))

def convertOldSlivers ():
  s = select([t_slivers])
  conn = db_session.connection()
  result = conn.execute(s)
  for row in result:
    try:
      sliver = {}
      sliver["slice_urn"] = row[t_slivers.c.slice_urn]
      sliver["sliver_urn"] = row[t_slivers.c.sliver_urn]
      sliver["fvslicename"] = row[t_slivers.c.fvslicename]
      sliver["req_rspec"] = row[t_slivers.c.req_rspec]
      sliver["manifest_rspec"] = row[t_slivers.c.manifest_rspec]
      obj = row[t_slivers.c.parsed_obj]
      expdt = row[t_slivers.c.expiration]
      exp = time.mktime(expdt.timetuple()) + expdt.microsecond / 1E6
      sliver["exp"] = exp
      sliver["priority"] = row[t_slivers.c.priority]
      sliver["status"] = row[t_slivers.c.status]
      sliver["deleted"] = row[t_slivers.c.deleted]
      importSliver(sliver)
    except Exception, e:
      print "Exception importing sliver!"
      print str(e)
      continue
  

def convertOldConfig ():
  s = select([t_config])
  conn = db_session.connection()
  result = conn.execute(s)
  for row in result:
    k = row[t_config.c.key]
    v = row[t_config.c.value]
    if k == "cert_dir":
      setNewConfig("geni.cert-dir", v)
    elif k == "site_tag":
      setNewConfig("geni.site-tag", v)
    elif k == "flowvisor_info":
      setNewConfig("flowvisor.hostname", v["host"])
      setNewConfig("flowvisor.json-port", v["json_port"])
      setNewConfig("flowvisor.xmlrpc-port", v["xmlrpc_port"])
      setNewConfig("flowvisor.passwd", v["passwd"])
    elif k == "max_lease":
      setNewConfig("geni.max-lease", (v.days*24))
    elif k == "admin_email":
      setNewConfig("email.admin-addr", v)
    elif k == "email_info":
      setNewConfig("email.smtp-server", v["smtp_server"])
      setNewConfig("email.from", v["from"])
      setNewConfig("email.reply-to", v["reply-to"])
      
def importSliver (sliver):
  print "Importing sliver [%s]" % (sliver["sliver_urn"])
#  pprint.pprint(sliver)
  data = connect(IMPORTURL, "foamadmin", "admin", sliver)

def setNewConfig (key, value):
  print "Setting config [%s] as [%s]" % (key, value)
  obj = {"key" : key, "value" : value}
  data = connect(CONFIGURL, "foamadmin", "admin", obj)
#  outputJSON(data)

def setAdminPassword ():
  newpass = getpass.getpass("New foamadmin password: ")
  obj = {"passwd" : newpass}
  print "Setting password for user 'foamadmin'"
  data = connect("https://localhost:3626/core/auth/set-admin-passwd", "foamadmin", "admin", obj)
  outputJSON(data)

def beginImport ():
  data = connect("https://localhost:3626/core/admin/begin-import", "foamadmin", "admin")

def finishImport ():
  data = connect("https://localhost:3626/core/admin/finish-import", "foamadmin", "admin")

#### Utilities
def connect (url, user, passwd, data = None):
  try:
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, user, passwd)
    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    opener = urllib2.build_opener(authhandler)

    if data is not None:
      data = json.dumps(data)

      h = {"Content-Type" : "application/json"}
      req = urllib2.Request(url, data, h)
      ph = opener.open(req)
      return ph.read()
    else:
      req = urllib2.Request(url)
      ph = opener.open(req)
      return ph.read()

  except urllib2.HTTPError, e:
    if e.code == 401:
      print "Basic auth failed: invalid password"
      sys.exit(1)
    elif e.code == 504:
      print "HTTP Error 504: Gateway Time-out"
      sys.exit(1)
    else:
      print e
  except RuntimeError, e:
    print e


def outputJSON (data, exit=False):
  j = json.loads(data)
  try:
    if j["retcode"] != 0:
      print j["msg"]
      if j["value"].has_key("missing"):
        print "Missing: %s" % (j["value"]["missing"])
        print "Incorrect Type: %s" % (j["value"]["wrong-type"])
      if exit:
        sys.exit(1)
      return
  except Exception:
    pass

  if j["value"] is None:
    return

  json.dump(j["value"], sys.stdout, indent=1)
  print
  if exit:
    sys.exit()

### Main
if __name__ == '__main__':
  beginImport()
  convertOldConfig()
  convertOldSlivers()
  finishImport()
  setAdminPassword()
  
