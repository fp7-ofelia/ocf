import os, sys
sys.path.insert(0, '/opt/ofreg')
sys.path.insert(0, '/opt/ofreg/ofreg')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ofreg.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

