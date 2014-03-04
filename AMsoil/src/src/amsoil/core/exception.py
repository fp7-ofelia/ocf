import logging

class CoreException(Exception):
  def __init__ (self):
    self._logged = False

  def log(self, logh, msg, level = logging.ERROR):
    logh.log(level, msg)
    self._logged = True


#Derived exceptions
class NotImplementedError(CoreException):
    pass
class NoProviderAvailableError(CoreException):
    pass

