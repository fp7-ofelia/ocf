import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '../../../python')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'expedient.clearinghouse.settings'

# changed 19.04.2011, ak, tr
#sys.path.append(PYTHON_DIR)
sys.path.insert(0, PYTHON_DIR)

from django.contrib.auth.models import User
from django import db
from expedient.clearinghouse.settings import ROOT_PASSWORD, ROOT_USERNAME
from expedient.clearinghouse.aggregate.models import *

def check_password(environ, user, password):
    db.reset_queries() 

    kwargs = {'username': user, 'is_active': True}
    
    try: 
        if environ['REQUEST_URI'] == '/vt_plugin/xmlrpc/vt_am/':
            for agg in Aggregate.objects.all():
                agg = agg.as_leaf_class()
                if agg.leaf_name == 'VtPlugin' and user == agg.client.username and password == agg.client.password:
                    return True
            return False
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
