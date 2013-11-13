# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

from foam.core.log import KeyAdapter
from foam.config import XMLRPC_LOGPARAMS

class Dispatcher(object):
  def __init__ (self, key, log):
    self._key = key
    self._log = KeyAdapter(key, log)

  def _dispatch (self, method, params):
    self._log.info("Called: <%s>" % (method))
    if XMLRPC_LOGPARAMS:
      self._log.debug("Parameters: <%s>" % (str(params)))

    try:
      meth = getattr(self, "pub_%s" % (method))
    except AttributeError, e:
      self._log.warning("Client called unknown method: <%s>" % (method))

    try:
      return meth(*params)
    except Exception, e:
      if not hasattr(e, "_foam_logged"):
        self._log.exception("Call to known method <%s> failed!" % (method))
      raise Exception(str(e))
 
