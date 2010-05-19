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
TESTS_DIR = join(EGENI_DIR, "tests/src/python/tests")
GCF_DIR = join(EGENI_DIR, "gcf/src")
SSL_DIR = join(dirname(__file__), "../ssl")

sys.path.append(join(TESTS_DIR, ".."))
sys.path.append(join(OM_PROJECT_DIR, ".."))
sys.path.append(join(CH_PROJECT_DIR, ".."))
sys.path.append(GCF_DIR)

USE_RANDOM = False

HOST = socket.getfqdn()
HOST_IP = socket.gethostbyname(HOST)
OM_PORT = 8443
CH_PORT = 443

FLOWVISORS = [
    dict(
        host=HOST_IP,
        of_port=6633,
        xmlrpc_port=8080,
        username="root",
        password="rootpassword"
    ),
]
MININET_VMS = ["192.168.188.129"]

NUM_EXPERIMENTS = 2

# basic settings sanity checks
assert(len(FLOWVISORS) == len(MININET_VMS))
