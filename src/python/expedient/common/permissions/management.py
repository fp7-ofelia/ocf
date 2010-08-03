'''
Created on Jun 2, 2010

@author: jnaous
'''
from django.utils.importlib import import_module
from django.db.models import signals

def _import_module(name, app_name):    
    # Below is copied and modified from django's syncdb command.
    # Import the module within each installed app, to register
    # permissions
    try:
        import_module('.%s' % name, app_name)
    except ImportError, exc:
        # This is slightly hackish. We want to ignore ImportErrors
        # if the "management" module itself is missing -- but we don't
        # want to ignore the exception if the management module exists
        # but raises an ImportError for some reason. The only way we
        # can do this is to check the text of the exception. Note that
        # we're a bit broad in how we check the text, because different
        # Python implementations may not use the same text.
        # CPython uses the text "No module named management"
        # PyPy uses "No module named myproject.myapp.management"
        msg = exc.args[0]
        if not msg.startswith('No module named') or name not in msg:
            raise

def post_syncdb_run(sender, **kwargs):
    # We need to wait until the permissions application is
    # installed (syncdb'd)
    if post_syncdb_run.installed_permissions:
        _import_module("permissions", sender.__name__.split(".models")[0])

    # If the permissions app is was just installed, then import the
    # permissions of any queued application
    elif sender.__name__.startswith("expedient.common.permissions"):
        post_syncdb_run.installed_permissions = True
        for mod in post_syncdb_run.waiting_for_permissions:
            _import_module("permissions", mod.__name__.split(".models")[0])
    
    # Otherwise, queue this application until the permissions app
    # is installed
    else:
        post_syncdb_run.waiting_for_permissions.append(sender)

post_syncdb_run.waiting_for_permissions = []
post_syncdb_run.installed_permissions = False

signals.post_syncdb.connect(post_syncdb_run)
