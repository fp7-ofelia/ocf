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

# Randomize the tests where possible?
USE_RANDOM = False

# Address and ports of the expedient clearinghouse and opt-in manager
HOST = socket.getfqdn()
OM_PORT = 8443
CH_PORT = 443

PREFIX = ""

# Information about where the test flowvisor should run
FLOWVISORS = [
    dict(
        host="172.16.77.1",       # IP address for flowvisor's interface
        of_port=6633,             # openflow port
        xmlrpc_port=8080,         # XMLRPC port for the flowvisor
        username="root",          # The username to use to connect to the FV
        password="password",      # The password to use to connect to the FV
        path=(FLOWVISOR_DIR, "default-config.xml"), # configuration file
    ),
]
MININET_VMS = ["172.16.77.130"]   # IP address of the mininet VM

CONTROLLER_HOST = "localhost"     # hostname for test controller
CONTROLLER_PORT = "16633"         # port for test controller

NUM_EXPERIMENTS = 2               # Number of Slices

NUM_DUMMY_OMS = 3                 # Number of Dummy OMs to use for GAPI tests.
NUM_SWITCHES_PER_AGG = 10         # Number of dummy switches for GAPI tests
NUM_LINKS_PER_AGG = 20            # Number of dummy links for GAPI tests

NUM_DUMMY_FVS = 1                 # Don't change. Num of Dummy FVs for OM tests

USE_HTTPS = True                  # Run using HTTPS or HTTP to expedient & OM?
                                  # WARNING: This is experimental and untested

SHOW_PROCESSES_IN_XTERM = True    # If set to True, processes run as part of
                                  # the test suites will popup on separate
                                  # xterms. xterm must be installed.

PAUSE_AFTER_TESTS = False         # If true, each test will wait for an Enter
                                  # from the user before tearing down (useful
                                  # to look at xterm output).

# basic settings sanity checks
assert(len(FLOWVISORS) == len(MININET_VMS))

from expedient.common import loggingconf
import logging
loggingconf.set_up(logging.DEBUG) # Change logging.INFO for less output
