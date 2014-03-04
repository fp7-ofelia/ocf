"""
This module provides logging facilities. More specifically, it provides a way to get to a (configured) python logger.
Hence the interface of this logger is the same as the python one (so please direct all complaints regarding this to the python people). 
In order to get such a logger instance, you could insert this code at the beginning of your module:
    import amsoil.core.log
    logger=amsoil.core.log.getLogger('SOMENAME')
whereby SOMENAME represents an optional prefix for the logging messages (e.g. 'xplugin' would yield messages like 'd.a.te [xplugin] message')

Configuration
Please see the config.py file in the root/src-folder.

Rationale
After long discussions logging is a core service.
The main reason for having logging as a core service is that the pluginmanager should be
able to log straight away (without loading a dedicated plugin). Also the administrator should have only one place to
edit the log config (level, file, etc.). If you had a plugin for it, the config-plugin-service would not be available
when the pluginmanager loads.
"""
import logging, logging.handlers

from amsoil import config

LOGGER_NAME = 'amsoil'

def getLogger(prefix=None):
    """Receive a python logger (logging.Logger) which has been configured by AMsoil."""
    logger = logging.getLogger(LOGGER_NAME)
    if (prefix):
        return PrefixAdapter(logger, prefix)
    else:
        return logger


class PrefixAdapter(logging.LoggerAdapter):
    """Internal class for wrapping logging messages. Do not use outside this module."""
    def __init__(self, logger, prefix):
        logging.LoggerAdapter.__init__(self, logger, { "prefix" : prefix })

    def process(self, msg, kwargs):
        prefix = self.extra["prefix"]
        return ("[%s] %s" % (prefix, msg), kwargs)
        
# initialziation
lhandle = logging.handlers.RotatingFileHandler(config.LOG_FILE, maxBytes = 1000000)
lhandle.setLevel(config.LOG_LEVEL)
lhandle.setFormatter(logging.Formatter(config.LOG_FORMAT))
logger = getLogger()
logger.addHandler(lhandle)
logger.setLevel(config.LOG_LEVEL)
logger.info("Logging initialized")
