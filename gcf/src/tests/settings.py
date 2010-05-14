'''
Created on May 11, 2010

@author: jnaous
'''
from os.path import join, dirname, basename
import socket

SRC_DIR = join(dirname(__file__), "../../")
FIXTURES_DIR = join(dirname(__file__), "fixtures")
SSL_DIR = join(dirname(__file__), "ssl")
CH_PROJECT_DIR = join(dirname(__file__), "../../../v2/src/python/clearinghouse")
GCF_DIR = join(dirname(__file__), "../")

NUM_DUMMY_OMS = 3
NUM_SWITCHES_PER_AGG = 10
NUM_LINKS_PER_AGG = 10

HOST = socket.getfqdn()
PORT = 443
PREFIX = ""
