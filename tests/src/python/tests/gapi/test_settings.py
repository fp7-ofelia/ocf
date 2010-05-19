'''
Created on May 11, 2010

@author: jnaous
'''
from os.path import join, dirname, basename
import socket
import sys

SSL_DIR = join(dirname(__file__), "../ssl")
EGENI_DIR = join(dirname(__file__), "../../../../../")
CH_PROJECT_DIR = join(EGENI_DIR, "v2/src/python/clearinghouse")
GCF_DIR = join(EGENI_DIR, "gcf/src")

NUM_DUMMY_OMS = 3
NUM_SWITCHES_PER_AGG = 10
NUM_LINKS_PER_AGG = 20

HOST = socket.getfqdn()
PORT = 443
PREFIX = ""

sys.path.append(GCF_DIR)
sys.path.append(join(CH_PROJECT_DIR, ".."))
