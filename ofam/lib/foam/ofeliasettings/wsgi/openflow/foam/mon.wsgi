import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '../../../../../foam')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'ofeliasettings.openflow.foam.settings'

sys.path.insert(0,PYTHON_DIR)

from ofeliasettings.openflow.foam.monitoring.BackgroundMonitor import BackgroundMonitor
BackgroundMonitor.monitor()

