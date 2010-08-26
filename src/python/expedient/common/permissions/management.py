'''
Created on Jun 2, 2010

@author: jnaous
'''
from django.utils.importlib import import_module
from django.db.models import signals
from django.conf import settings
import logging

logger = logging.getLogger("permissions.management")

# XXX: Hack!
def post_syncdb_run(sender, **kwargs):
    """Look for permissions.run in each app and call it.
    
    This function will wait till the last installed app, and then
    search for all permissions modules, and try to call a C{run} function
    in them if found.
    """
    post_syncdb_run.queued = getattr(post_syncdb_run, "processed", [])
    post_syncdb_run.perms_installed = getattr(
        post_syncdb_run, "perms_installed", False)

    app = sender.__name__.split(".models")[0]

    # installed!
    if app == "expedient.common.permissions":
        post_syncdb_run.perms_installed = True
        
    post_syncdb_run.queued.append(app)

    # need to wait until we syncdb the permissions app
    if post_syncdb_run.perms_installed:
        for app in post_syncdb_run.queued:
            logger.debug("Checking app %s for permissions" % app)
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
                logger.debug("Ran permissions.run() for %s" % app)
            except AttributeError as exc:
                msg = "%s" % exc
                if msg == "'module' object has no attribute 'run'":
                    logger.warn(
                        "Function called 'run' missing from %s.permissions."\
                        " Skipping." % app
                    )
                else:
                    raise
        post_syncdb_run.queued = []

signals.post_syncdb.connect(post_syncdb_run)
