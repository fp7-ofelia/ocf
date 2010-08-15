'''
Created on Jun 15, 2010

@author: jnaous
'''
from django.contrib.auth.backends import RemoteUserBackend
import logging

logger = logging.getLogger("backends.remoteuser")

class NoCreateRemoteUserBackend(RemoteUserBackend):
    """
    Extends the RemoteUserBackend by simply setting C{create_unknown_user} to
    False instead of the default True, so that unknown users are not created.
    """
    create_unknown_user = False
