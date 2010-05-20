'''
Created on May 11, 2010

@author: jnaous
'''
from os.path import join, dirname
import socket
import sys

PYTHON_DIR = join(dirname(__file__), "../../../../")
CH_PROJECT_DIR = join(PYTHON_DIR, "expedient/clearinghouse")
GCF_DIR = join(PYTHON_DIR, "gcf")
SSL_DIR = join(dirname(__file__), "../ssl")

print "********", CH_PROJECT_DIR

NUM_DUMMY_OMS = 3
NUM_SWITCHES_PER_AGG = 10
NUM_LINKS_PER_AGG = 20

HOST = socket.getfqdn()
PORT = 443
PREFIX = ""
