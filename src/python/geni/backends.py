'''
Created on Aug 12, 2010

@author: jnaous
'''
import logging
import re
from django.contrib.auth.backends import RemoteUserBackend
from django.conf import settings
from expedient.common.permissions.shortcuts import give_permission_to
from django.contrib.auth.models import User

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

class MagicWordBackend(object):
    """Authenticates users if the magic word "MagicWord" is given as credentials"""
    
    MAGIC_WORD = "MagicWord"
    
    def authenticate(self, magicword=None, user=None):
        if magicword == self.MAGIC_WORD:
            return user
        else:
            return None