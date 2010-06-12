'''
Created on May 15, 2010

@author: jnaous
'''
from os.path import join, dirname
import socket, sys

PYTHON_DIR = join(dirname(__file__), "../../")
OM_PROJECT_DIR = join(PYTHON_DIR, "openflow/optin_manager")
CH_PROJECT_DIR = join(PYTHON_DIR, "expedient/clearinghouse")
GCF_DIR = join(PYTHON_DIR, "gcf")
SSL_DIR = join(dirname(__file__), "ssl")
FLOWVISOR_DIR = join(PYTHON_DIR, "../../../flowvisor")

USE_RANDOM = False

HOST = socket.getfqdn()
OM_PORT = 8443
CH_PORT = 443

PREFIX = ""

FLOWVISORS = [
    dict(
        host="192.168.188.1",
        of_port=6633,
        xmlrpc_port=8080,
        username="root",
        password="rootpassword",
        path=(FLOWVISOR_DIR, "default-config.xml"),
    ),
]
MININET_VMS = ["192.168.188.131"]

NUM_EXPERIMENTS = 2

NUM_DUMMY_OMS = 3
NUM_SWITCHES_PER_AGG = 10
NUM_LINKS_PER_AGG = 20

NUM_DUMMY_FVS = 1

# basic settings sanity checks
assert(len(FLOWVISORS) == len(MININET_VMS))
