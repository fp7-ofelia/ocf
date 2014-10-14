import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '../../python')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'vt_manager.settings.settingsLoader'

sys.path.insert(0,PYTHON_DIR)
from vt_manager.controller.monitoring.BackgroundMonitor import BackgroundMonitor
from vt_manager.controller.monitoring.background_expiration_monitoring import BackgroundExpirationMonitoring
from vt_manager.controller.monitoring.backgroundreservation import BackgroundReservationMonitoring


BackgroundMonitor.monitor()
BackgroundExpirationMonitoring.monitor()
BackgroundReservationMonitoring.monitor()
