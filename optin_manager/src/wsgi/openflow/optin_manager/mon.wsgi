import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '../../../python')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'openflow.optin_manager.settings'

#sys.path.append(PYTHON_DIR)
sys.path.insert(0,PYTHON_DIR)

# XXX UNCOMMENT EVERY PROCESS AND REMOVE THIS COMMENT

from openflow.optin_manager.monitoring.BackgroundMonitor import BackgroundMonitor
from openflow.optin_manager.monitoring.reservation import BackgroundReservationMonitoring
#from openflow.optin_manager.monitoring.background_expiration_monitoring import BackgroundExpirationMonitoring
# Remove expired reservations (from Allocate) and flowspaces (from Provision)
print "== OFAM: Running monitoring of expired reservations... =="
BackgroundReservationMonitoring.monitor()
print "== OFAM: Running monitoring of expired resources... =="
# Background process to monitor and remove expired sessions in Django ("Session" object)
BackgroundMonitor.monitor()
#bg_exp_mon = BackgroundExpirationMonitoring()
#bg_exp_mon.monitor()
