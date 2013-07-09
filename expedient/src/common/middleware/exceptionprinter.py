'''
Created on Aug 11, 2010

@author: jnaous
'''

import logging

logger = logging.getLogger("exceptionprinter")

class ExceptionPrinter(object):
    def process_exception(self, request, exception):
        logger.error("Got exception %s of type %s"
                     % (exception, type(exception)))
