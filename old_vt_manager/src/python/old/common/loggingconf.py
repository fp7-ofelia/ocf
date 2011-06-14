'''
Created on Jun 2, 2010

@author: jnaous
'''
import logging

def set_up(level):
    if not hasattr(logging, "setup_done"):
        if level == logging.DEBUG:
            format = '%(asctime)s:%(name)s:%(levelname)s\n    %(pathname)s:%(lineno)s\n    **** %(message)s'
        else:
            format = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
        logging.basicConfig(level=level, format=format)
    logging.setup_done = True
