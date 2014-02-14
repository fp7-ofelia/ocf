from amsoil.core.exception import CoreException

class ConfigUnknownConfigKey(CoreException):
  def __init__ (self, key):
    super(ConfigUnknownConfigKey, self).__init__()
    self.key = key

  def __str__ (self):
    return "Unknown config key '%s'" % (self.key)

class ConfigDuplicateConfigKey(CoreException):
  def __init__ (self, key):
    super(ConfigDuplicateConfigKey, self).__init__()
    self.key = key

  def __str__ (self):
    return "Duplicate config key '%s'" % (self.key)

