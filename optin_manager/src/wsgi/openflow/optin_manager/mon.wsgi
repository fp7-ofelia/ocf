import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '../../../python')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'openflow.optin_manager.settings'

#sys.path.append(PYTHON_DIR)
sys.path.insert(0,PYTHON_DIR)

from openflow.optin_manager.monitoring.BackgroundMonitor import BackgroundMonitor
from openflow.optin_manager.monitoring.background_expiration_monitoring import BackgroundExpirationMonitoring
BackgroundMonitor.monitor()
BackgroundExpirationMonitoring.monitor()

