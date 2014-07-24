'''
Created on Aug 12, 2010

@author: jnaous
'''
import logging
import traceback
from django.contrib.auth.backends import RemoteUserBackend
from expedient.common.federation.sfa.trust.gid import GID
from expedient.clearinghouse.geni.utils import get_user_urn, urn_to_username
from expedient.common.federation.geni.util.urn_util import URN

logger = logging.getLogger("geni.backends")

def get_username_from_cert(cert_string):
    try:
        gid = GID(string=cert_string)
        
        # extract the URN in the subjectAltName
        urn_str = gid.get_urn()
        
        logger.debug("URN: %s" % urn_str)
        
    except:
        logger.warn("Failed to get certificate from string.")
        logger.warn(traceback.format_exc())
        return cert_string
    
    try:
        urn = URN(urn=str(urn_str))
    except ValueError:
        return cert_string
    
    # check if this user is one of ours
    home_urn = get_user_urn(urn.getName())
    if home_urn == urn.urn_string():
        username = urn.getName()
    else:
        username = urn_to_username(urn.urn_string())
        
    logger.debug("Returning username %s" % username)
    
    return username

class GENIRemoteUserBackend(RemoteUserBackend):
    """
    Extends the RemoteUserBackend to create GENI users.
    """
    create_unknown_user = True

    def clean_username(self, username):
        return get_username_from_cert(username)

class MagicWordBackend(object):
    """Authenticates users if the magic word "MagicWord" is given as credentials"""
    
    MAGIC_WORD = "MagicWord"
    
    def authenticate(self, magicword=None, user=None):
        if magicword == self.MAGIC_WORD:
            return user
        else:
            return None
