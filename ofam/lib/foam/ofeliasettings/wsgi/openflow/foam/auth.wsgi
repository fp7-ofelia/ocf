import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '../../../../../foam')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'ofeliasettings.openflow.foam.settings'

sys.path.insert(0,PYTHON_DIR)

from django.contrib.auth.models import User
from django import db

def check_password(environ, user, password):
    db.reset_queries() 

    kwargs = {'username': user, 'is_active': True}
    
    try: 
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
