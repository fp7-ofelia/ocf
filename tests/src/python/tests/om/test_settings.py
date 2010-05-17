'''
Created on May 15, 2010

@author: jnaous
'''
from os.path import join, dirname, basename
import socket
import sys

EGENI_DIR = join(dirname(__file__), "../../../../../")
OM_PROJECT_DIR = join(EGENI_DIR, "om/src/python/optin_manager")
CH_PROJECT_DIR = join(EGENI_DIR, "v2/src/python/clearinghouse")

sys.path.append(join(OM_PROJECT_DIR, ".."))
sys.path.append(join(CH_PROJECT_DIR, ".."))

NUM_DUMMY_FVS = 1

USE_RANDOM = False

HOST = socket.getfqdn()
PORT = 8443
PREFIX = ""
