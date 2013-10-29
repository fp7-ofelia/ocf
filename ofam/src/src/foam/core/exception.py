import logging

class CoreException(Exception):
  def __init__ (self):
    self._foam_logged = False

  def log (self, logh, msg, level = logging.ERROR):
    logh.log(level, msg)
    self._foam_logged = True
