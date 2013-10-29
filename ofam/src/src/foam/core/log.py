import logging

class KeyAdapter(logging.LoggerAdapter):
  def __init__ (self, key, logger):
    logging.LoggerAdapter.__init__(self, logger, {"key" : key})

  def process (self, msg, kwargs):
    key = self.extra["key"]
    return ("[%s] %s" % (key, msg), kwargs)
