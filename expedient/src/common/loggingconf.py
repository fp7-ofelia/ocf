'''
Created on Jun 2, 2010

@author: jnaous
'''
import logging

def set_up(default_level, exception_levels=[]):
    """Setup logging for the system.
    
    @param default_level: The default logging level for all loggers.
    @param exception_levels: a list of tuples (logger name, logging level)
        to set the logging levels for particular loggers.
    """
    if not hasattr(logging, "setup_done"):
        if default_level == logging.DEBUG:
            format = '%(asctime)s:%(name)s:%(levelname)s\n    %(pathname)s:%(lineno)s\n    **** %(message)s'
        else:
            format = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
        logging.basicConfig(level=default_level, format=format)
        
    # Now for each tuple in exception_levels, override the default
    for name, level in exception_levels:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
    logging.setup_done = True
