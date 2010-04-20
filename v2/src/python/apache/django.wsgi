import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '../')

os.environ['DJANGO_SETTINGS_MODULE'] = 'clearinghouse.settings'

sys.path.append(PYTHON_DIR)

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
