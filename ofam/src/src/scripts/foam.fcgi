#!/usr/bin/python
# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

# import figleaf
# figleaf.start()

import sys
import datetime
import logging
import traceback

try:
  import foam.app
  foamlog = logging.getLogger('foam')
except Exception, e:
  # The log is *probably* already set up, because we do that really
  # early in foam.app import.  If we can't write the file though,
  # this isn't going to be very revealing, so we still print the
  # exception to the console
  foamlog = logging.getLogger('foam')
  foamlog.exception(e)

  traceback.print_exception(e)
  sys.exit(1)
  

from flup.server.fcgi import WSGIServer
import foam.version
from foam.config import FOAMLOG, PLUGINROOT
from foam.plugin_manager import PluginManager


if __name__ == '__main__':
  try:
    foamlog.info("[FOAM] Version: %s" % (foam.version.VERSION))
    foamlog.debug("[FOAM] Path: %s" % (":".join(sys.path)))

    pm = PluginManager(PLUGINROOT)
    foam.app.init(pm)
    WSGIServer(foam.app.app, bindAddress='/tmp/foam.sock').run()
  except Exception, e:
    foamlog.exception(e)
