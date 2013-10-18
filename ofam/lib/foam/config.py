# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

import logging

FOAM_ROOT = "/opt/ofelia/ofam"

DB_PATH = "%s/db/geni-openflow.db" % (FOAM_ROOT)
CONFIGDB_PATH = "%s/db/config.db" % (FOAM_ROOT)

DB_ENGINE = "sqlite:///%s" % (DB_PATH)
CONFIGDB_ENGINE = "sqlite:///%s" % (CONFIGDB_PATH)

HTPASSWDFILE = "%s/etc/users.htpasswd" % (FOAM_ROOT)
GENICERTDIR = "%s/etc/gcf-ca-certs" % (FOAM_ROOT)

OFNSv3 = "%s/schemas" % (FOAM_ROOT)
OFNSv4 = "%s/schemas" % (FOAM_ROOT)
PGNS = "%s/schemas" % (FOAM_ROOT)
XSNS = "http://www.w3.org/2001/XMLSchema-instance"

LOGLEVEL = logging.INFO
LOGFORMAT = "%(asctime)s [%(levelname)s] - %(message)s"
LOGDIR = "%s/log" % (FOAM_ROOT)
FOAMLOG = "%s/foam.log" % (LOGDIR)

PLUGINROOT = "%s/plugins" % (FOAM_ROOT)

TASKLOGDIR = "%s/tasks/" % (LOGDIR)
TASK_QUEUE_DIR = "%s/tasks/queue" % (FOAM_ROOT)
TASK_COMPLETED_DIR = "%s/tasks/completed" % (FOAM_ROOT)

TEMPLATE_DIR = "%s/etc/templates/default" % (FOAM_ROOT)
USER_TEMPLATE_DIR = "%s/etc/templates/custom" % (FOAM_ROOT)

XMLRPC_LOGPARAMS = False

# Typically local policy things
AUTO_SLIVER_PRIORITY = 2000
REQUIRE_SLIVER_EMAIL = True

GAPI_REPORTFOAMVERSION = True

try:
  from foamext.config import *
except ImportError:
  pass
