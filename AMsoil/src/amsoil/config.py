"""
This file contains the bare minimum for bootstrapping AMsoil.
All (non core) implementations/plugins should use the config service/plugin.
"""

import logging
import os.path

##Paths
SRC_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
ROOT_PATH = os.path.normpath(os.path.join(SRC_PATH, '..'))
PLUGINS_PATH = os.path.join(SRC_PATH, 'plugins')

##Logging
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s [%(levelname)s] - %(message)s"
LOG_FILE = "%s/log/amsoil.log" % (ROOT_PATH,)

##CONFIGDB
CONFIGDB_PATH = "%s/deploy/config.db" % (ROOT_PATH,)
CONFIGDB_ENGINE = "sqlite:///%s" % (CONFIGDB_PATH,)
IS_MULTIPROCESS = True

##IPC related parameters
#IPC_RABBITMQ_SERVER="localhost"
# IPC_RABBITMQ_SERVER="192.168.0.218"
##IPC: uncomment to use user/password
#IPC_RABBITMQ_USERNAME="user"
#IPC_RABBITMQ_PASSWORD="pass"


def expand_amsoil_path(path):
    """If the given path is relative, the path will be made absolute, starting from AMsoil's root."""
    path = os.path.expanduser(path)
    if os.path.isabs(path):
        return path
    else:
        return os.path.normpath(os.path.join(ROOT_PATH, path))
