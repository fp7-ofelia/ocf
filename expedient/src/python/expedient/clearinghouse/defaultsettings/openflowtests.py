'''Contains default settings for the testing environment.
Created on Aug 22, 2010

@author: jnaous
'''
from os.path import join, dirname

PYTHON_DIR = join(dirname(__file__), "../../..")
OM_PROJECT_DIR = join(PYTHON_DIR, "openflow/optin_manager")
CH_PROJECT_DIR = join(PYTHON_DIR, "expedient/clearinghouse")
GCF_DIR = join(PYTHON_DIR, "gcf")
SSL_DIR = join(dirname(__file__), "ssl")

FLOWVISOR_DIR = join(PYTHON_DIR, "../../../../flowvisor")
'''Location of the testing Flowvisor source directory.'''

USE_RANDOM = False
'''Randomize the tests where possible?'''

SITE_IP_ADDR = '192.168.126.128'
'''The IP address of the host where Expedient and the OM are running.'''

OM_PORT = 8443
'''Port on which the Opt-In manager is running.'''

CH_PORT = 443
'''Port on which Expedient is running.'''

PREFIX = ""

FV_CONFIG = 'fv_vm_config.xml'
'''Name of the Flowvisor config file.'''

GCH_PORT = 8001
'''The port on which the GENI Clearinghouse should run.'''

FLOWVISORS = [
    dict(
        of_port=6633,             # openflow port
        xmlrpc_port=8080,         # XMLRPC port for the flowvisor
        username="root",          # The username to use to connect to the FV
        password='rootpassword',  # The password to use to connect to the FV
        path=(FLOWVISOR_DIR, FV_CONFIG), # configuration file
    ),
]
'''Information about where the test flowvisor should run.

This should be a list of dicts with the following keys:

    - C{of_port}: The openflow port number the Flowvisor will use.
    - C{xmlrpc_port}: The port number for XMLRPC calls to the Flowvisor.
    - C{username}: The username to use for accessing the xmlrpc calls.
    - C{password}: The password to use for accessing the xmlrpc calls.
    - C{path}: The location of the flowvisor config file.

'''

MININET_VMS = [('172.16.77.131', 22)]
'''Information about where the Mininet VM is running.

This should be a list of tuples (IP address, SSH port number)

'''

MININET_SWITCH_TYPE = "user"
'''Type of switch to use. One of "user", "ovsk", "kernel"'''

NUM_EXPERIMENTS = 2
'''Number of Slices to instantiate during testing.'''

NUM_DUMMY_OMS = 3
'''Number of Dummy OMs to use for GAPI tests.'''

NUM_SWITCHES_PER_AGG = 10
'''Number of dummy switches for GAPI tests.'''

NUM_LINKS_PER_AGG = 20
'''Number of dummy links for GAPI tests.'''

NUM_DUMMY_FVS = 1
'''Don't change. Num of Dummy FVs for OM tests.'''

USE_HTTPS = True
'''Run using HTTPS or HTTP to expedient & OM?'''

SHOW_PROCESSES_IN_XTERM = True
'''Don't change. Should forked processes run in an xterm?'''

PAUSE_AFTER_TESTS = False
'''If true, each test will wait for an Enter from the user
before tearing down (useful to look at xterm output).

'''

TIMEOUT = 20
'''Time to wait for processes to run and for communication to work.'''

# basic settings sanity checks
assert(len(FLOWVISORS) == len(MININET_VMS))
