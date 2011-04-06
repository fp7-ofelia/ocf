import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '../../../python')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'expedient.clearinghouse.settings'

sys.path.append(PYTHON_DIR)

from expedient.clearinghouse.monitoring.BackgroundMonitor import BackgroundMonitor
BackgroundMonitor.monitor()
