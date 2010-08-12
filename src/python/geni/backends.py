'''
Created on Aug 12, 2010

@author: jnaous
'''
import logging
import re
from django.contrib.auth.backends import RemoteUserBackend
from django.conf import settings

logger = logging.getLogger("geni.backends")

urn_matcher = re.compile(r"(?P<prefix>.*)\+(?P<role>.*)\+(?P<name>.*)")

class GENIRemoteUserBackend(RemoteUserBackend):
    """
    Extends the RemoteUserBackend to create GENI users.
    """
    create_unknown_user = True

    def clean_username(self, username):
        logger.debug("Cleaning username %s" % username)
        
        match = urn_matcher.match(username)
        if match:
            if match.group("prefix") == settings.GCF_URN_PREFIX:
                username = match.group("name")
            else:
                username = match.group("name")+"@"+match.group("prefix")
            return username
        else:
            return username
    