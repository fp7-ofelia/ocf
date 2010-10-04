'''
Created on Aug 12, 2010

@author: jnaous
'''
import logging
import re
from django.contrib.auth.backends import RemoteUserBackend
from gcf.sfa.trust.gid import GID
import traceback
from gcf.sfa.util.namespace import URN_PREFIX
from django.contrib.auth.models import User

logger = logging.getLogger("geni.backends")

urn_matcher = re.compile(URN_PREFIX+"\+"+r"(?P<prefix>.*)\+(?P<role>.*)\+(?P<name>.*)")

def urn_to_username(urn):
    """Create a valid username from a URN.
    
    This creates the username by taking the authority part of
    the URN, and the name part of the URN and joining them with "@".
    
    Any characters other than letters, digits, '@', '-', '_', '+', and '.'
    are replace with '_'.
    
    e.g. "urn:publicid:IDN+stanford:expedient%26+user+jnaous" becomes 
    "jnaous@expedient_26.stanford"
    
    The authority part of the URN is truncated to 150 characters, and the
    name part is truncated to 100 characters.
    
    @param urn: a urn to turn into a username
    @type urn: C{str}
    @return: a valid username
    @rtype: C{str}
    """
    
    invalid_chars_re = re.compile(r"[^\w@+.-]")
    
    m = urn_matcher.search(urn)
    if not m:
        return urn
    
    auth = m.group("prefix")
    auth = auth.split(":")
    auth.reverse()
    auth = ".".join(auth)
    if len(auth) > 150:
        auth = auth[:150]
        
    name = m.group("name")
    if len(name) > 100:
        name = name[:100]
        
    username = name + "@" + auth
    
    # replace all invalid chars with _
    username = invalid_chars_re.sub("_", username)
    
    assert(len(username) <= User._meta.get_field_by_name('username')[0].max_length)
    
    return username

class GENIRemoteUserBackend(RemoteUserBackend):
    """
    Extends the RemoteUserBackend to create GENI users.
    """
    create_unknown_user = True

    def clean_username(self, username):
        try:
            # The username field should be the full certificate
            gid = GID(string=username)
            logger.debug("Getting username from %s" % gid.dump())
            
            # extract the URN in the subjectAltName
            urn_str = gid.get_urn()
        except:
            logger.warn("Failed to get certificate from username.")
            logger.warn(traceback.format_exc())
            return username
        
        username = urn_to_username(urn_str)
        
        return username

class MagicWordBackend(object):
    """Authenticates users if the magic word "MagicWord" is given as credentials"""
    
    MAGIC_WORD = "MagicWord"
    
    def authenticate(self, magicword=None, user=None):
        if magicword == self.MAGIC_WORD:
            return user
        else:
            return None