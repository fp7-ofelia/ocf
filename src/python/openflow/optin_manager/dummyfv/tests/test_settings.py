'''
Created on May 15, 2010

@author: jnaous
'''
from os.path import join, dirname, basename
import socket
import sys

PYTHON_DIR = join(dirname(__file__), "../../../../")
OM_PROJECT_DIR = join(PYTHON_DIR, "openflow/optin_manager")

NUM_DUMMY_FVS = 1

USE_RANDOM = False

HOST = socket.getfqdn()
PORT = 8443
PREFIX = ""
