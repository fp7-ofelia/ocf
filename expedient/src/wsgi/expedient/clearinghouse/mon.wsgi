import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '../../../python')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'expedient.clearinghouse.settings'

#sys.path.append(PYTHON_DIR)
sys.path.insert(0,PYTHON_DIR)

from expedient.clearinghouse.monitoring.BackgroundMonitor import BackgroundMonitor
#from django.contrib.auth.models import User
#from django.contrib.auth import authenticate
#from expedient.clearinghouse.settings import ROOT_USERNAME, ROOT_PASSWORD
#try:
#    monUser = User.objects.get(first_name = 'monitor')
#except:
#    monUser = User.objects.create_user('monitor', 'monitor@gmail.com', 'monitor')
#    monUser.is_superuser = True
#    monUser.save()
#
#user = authenticate(username='monitor', password='monitor')
#user = authenticate(username=ROOT_USERNAME, password=ROOT_PASSWORD)
BackgroundMonitor.monitor()
