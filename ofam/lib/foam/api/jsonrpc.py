# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

from foam.core.log import KeyAdapter

def route (path, methods):
  def decorator (target):
    target.route = ((path, methods))
    return target
  return decorator

class Dispatcher(object):
  def __init__ (self, key, logger, app):
    self._log = KeyAdapter(key, logger)
    self._app = app

    for k in dir(self):
      try:
        val = getattr(self, k)
        (path, methods) = val.route
      except TypeError:
        continue
      except AttributeError:
        continue

      try:
        app.add_url_rule(path, path.replace("/", "_"), val, methods=methods)
        self._log.debug("Added route for: %s with method <%s>" % (path, k))
      except Exception, e:
        self._log.exception("Adding URL Rule")
        continue
