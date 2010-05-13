'''
Created on May 11, 2010

@author: jnaous
'''
from os.path import join, dirname, basename
import socket

SRC_DIR = join(dirname(__file__), "../../")

CA_KEY_LOCATION = "/etc/apache2/ssl.key/ca.key"
CA_CERT_LOCATION = "/etc/apache2/ssl.crt/ca.crt"
APACHE_CONFIG_LOCATION = "/etc/apache2/vhosts.d"

CLEARINGHOUSE_PROJECT_PATH = join(SRC_DIR, "../../v2/src/python/clearinghouse")
DUMMY_OM_PROJECT_PATH = join(SRC_DIR, "python/dummyom")

HOST = socket.getfqdn()
PORT_START = 8001

DUMMY_VHOST_PREFIX = "dummyom"

VHOST_CONFIG_LOCATION = join(SRC_DIR, "config/vhost-tests.conf")
SSL_DIR = join(dirname(__file__), "ssl")
DB_FIXTURE_DIR = join(dirname(__file__), "fixtures")

CLEARINGHOUSE_FIXTURE = join(DB_FIXTURE_DIR, "clearinghouse.json")
CLEARINGHOUSE_BACKUP_FIXTURE = join(DB_FIXTURE_DIR, "clearinghouse-backup.json")

DUMMY_OM_FIXTURE = join(DB_FIXTURE_DIR, "dummyom.json")
