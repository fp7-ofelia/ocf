# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University
# Copyright (c) 2012  Barnstormer Softworks

import logging
import logging.handlers
import os.path

from flask import Flask, request_started, request, request_tearing_down

from foam.config import FOAMLOG, LOGLEVEL, LOGFORMAT, LOGDIR

##############################################################
### We have to set up logging before child modules can use it
app = Flask("foam")

lhandle = logging.handlers.RotatingFileHandler('%s' % (FOAMLOG),
                                               maxBytes = 1000000, backupCount = 10)
lhandle.setLevel(LOGLEVEL)
lhandle.setFormatter(logging.Formatter(LOGFORMAT))
app.logger.addHandler(lhandle)
app.logger.setLevel(LOGLEVEL)

pl = logging.getLogger("perf")
plh = logging.handlers.RotatingFileHandler(os.path.normpath("%s/perf.log" % (LOGDIR)),
                                           maxBytes = 1000000, backupCount = 10)
plh.setLevel(logging.DEBUG)
plh.setFormatter(logging.Formatter("%(created)f [%(levelname)s] %(message)s"))
pl.addHandler(plh)
pl.setLevel(logging.DEBUG)

app.logger.info("[FOAM] Application Startup")
##############################################################

from foam.core.configdb import ConfigDB
from foam.geni.db import GeniDB

#request_tearing_down.connect(ConfigDB.close, app)
#request_tearing_down.connect(GeniDB.close, app)

from foam.api import auth
auth_apih = auth.setup(app) #Vasileios: get the returned apis

from foam.api import gapi1
gapi1_apih = gapi1.setup(app) #Vasileios: get the returned api handlers

from foam.api import debug
debug_apih = debug.setup(app) #Vasileios: get the returned api handlers

from foam.api import auto
auto_apih = auto.setup(app) #Vasileios: get the returned api handlers

from foam.api import admin
admin_apih = admin.setup(app) #Vasileios: get the returned api handlers

from foam.api import geni
geni_apih = geni.setup(app) #Vasileios: get the returned api handlers

#here check maybe ofelia-geni api collaboration

from foam.api import gapi2
gapi2_apih = gapi2.setup(app) #Vasileios: get the returned api handlers

#modified by Vasileios, load afterwards
#from foam.api import legacyexpgapi2
#legexpgapi2_apih = legacyexpgapi2.setup(app) #Vasileios: get the returned api handlers

#modified by Vasileios, load afterwards
from foam.api import legacyexpedientapi #Vasileios: get the returned api handlers
legacyexpedientapi_apih = legacyexpedientapi.setup(app) #Vasileios: get the returned api handlers

ConfigDB.commit()
GeniDB.commit()

def init (pm):
  pass
  #  for plugin in pm.getByInterface("foam.interface.rpc"):
  #  plugin.connect(app)

@request_started.connect_via(app)
def log_request (sender):
  app.logger.info("[REQUEST] [%s] <%s>" % (request.remote_addr, request.url))

