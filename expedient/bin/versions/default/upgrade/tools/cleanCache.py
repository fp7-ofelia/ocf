import os
import sys
from os.path import dirname, join
from django.conf import *

#configobj
try:
        from configobj import ConfigObj
except:
        #FIXME: ugly
        os.system("apt-get update && apt-get install python-configobj -y")
        from configobj import ConfigObj


# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

PYTHON_DIR = join(dirname(__file__), '../../../../../src/python')
PLUGINS_DIR = join(dirname(__file__), '../../../../../src/python/plugins')
os.environ['DJANGO_SETTINGS_MODULE'] = 'expedient.clearinghouse.settings'
#os.environ['DJANGO_SETTINGS_MODULE'] = sys.argv[2]
sys.path.insert(0,PLUGINS_DIR)
sys.path.insert(0,PYTHON_DIR)

from vt_plugin.models import resourcesHash
for rhash in resourcesHash.objects.all():
        rhash.delete()
