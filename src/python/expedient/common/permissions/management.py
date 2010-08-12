'''
Created on Jun 2, 2010

@author: jnaous
'''
from django.utils.importlib import import_module
from django.db.models import signals
from django.conf import settings
import logging

logger = logging.getLogger("permissions.management")

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

# XXX: Hack!
def post_syncdb_run(sender, **kwargs):
    """Look for permissions.run in each app and call it.
    
    This function will wait till the last installed app, and then
    search for all permissions modules, and try to call a C{run} function
    in them if found.
    """
    post_syncdb_run.processed = getattr(post_syncdb_run, "processed", 0)
    num_apps = len(settings.INSTALLED_APPS)
    
    # if this is the last app then install permissions for all apps
    if post_syncdb_run.processed == num_apps - 1:
        for app in settings.INSTALLED_APPS:
            try:
                mod = import_module("%s.permissions" % app)
            except ImportError as exc:
                msg = exc.args[0]
                if not msg.startswith('No module named') or\
                "permissions" not in msg:
                    raise
                else:
                    continue
            try:
                mod.run()
            except AttributeError as exc:
                msg = "%s" % exc
                if msg == "'module' object has no attribute 'run'":
                    logger.warn(
                        "Function called 'run' missing from %s.permissions."\
                        " Skipping." % app
                    )
                else:
                    raise
        del post_syncdb_run.processed
    else:
        post_syncdb_run.processed += 1

post_syncdb_run.waiting_for_permissions = []
post_syncdb_run.installed_permissions = False

signals.post_syncdb.connect(post_syncdb_run)
