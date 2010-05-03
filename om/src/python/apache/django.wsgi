import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '../')
CH_PYTHON_DIR = join(dirname(__file__), '../../../../v2/src/python')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'optin_manager.settings'

sys.path.append(PYTHON_DIR)
sys.path.append(CH_PYTHON_DIR)

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
