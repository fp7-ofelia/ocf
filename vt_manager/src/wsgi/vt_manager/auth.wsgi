import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '../../python')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'vt_manager.settings.settingsLoader'



#sys.path.append(PYTHON_DIR)
sys.path.insert(0,PYTHON_DIR)


from django.contrib.auth.models import User
from django import db
from vt_manager.settings.settingsLoader import XMLRPC_USER, XMLRPC_PASS

def check_password(environ, user, password):
    db.reset_queries()
    kwargs = {'username': user, 'is_active': True}

    try:
        if environ['REQUEST_URI'] == '/xmlrpc/plugin':
            if user == XMLRPC_USER and password == XMLRPC_PASS:
                return True
#            else:
#                return False
#        else:
        try:
            user = User.objects.get(**kwargs)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return True
        else:
            return False
    finally:
        db.connection.close()
