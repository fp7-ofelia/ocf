'''
Created on Jul 10, 2010

@author: jnaous
'''
from django.conf import settings
import os
import logging
from django.db.models import signals
from expedient.clearinghouse.geni.utils import get_ch_urn, create_x509_cert, create_slice_urn,\
    create_slice_credential
from expedient.common.federation.sfa.trust.gid import GID

logger = logging.getLogger("geni.management")

def create_expedient_certs():
    """
    Create the expedient certificate and keys for use in GENI API.
    """
    urn = get_ch_urn()
    create_x509_cert(
        urn, settings.GCF_X509_CH_CERT, settings.GCF_X509_CH_KEY, True)

def create_null_slice_cred():
    """Create a slice cred that can be used to list resources."""
    slice_urn = create_slice_urn()
    slice_gid, _ = create_x509_cert(slice_urn) 
    user_gid = GID(filename=settings.GCF_X509_CH_CERT)
    ucred = create_slice_credential(user_gid, slice_gid)
    ucred.save_to_file(settings.GCF_NULL_SLICE_CRED)

def _mkdirs(dirname):
    try:
        os.makedirs(dirname)
    except OSError as e:
        if "File exists" in e:
            pass
        else:
            raise

# Check if we already have cert and keys created for expedient
def check_and_create_auth(sender, **kwargs):
    """
    Check to see if the gid cert, keys, and credentials are readable, and
    create them if not.
    """
    
    _mkdirs(settings.GCF_X509_TRUSTED_CERT_DIR)
    _mkdirs(settings.GCF_X509_USER_CERT_DIR)
    _mkdirs(settings.GCF_X509_KEY_DIR)
    _mkdirs(settings.GCF_X509_CRED_DIR)
    
    if not os.access(settings.GCF_X509_CH_CERT, os.R_OK) or\
    not os.access(settings.GCF_X509_CH_KEY, os.R_OK):
        logger.info("Creating GENI API certificate and key.")
        create_expedient_certs()
    
#    if not os.access(settings.GCF_NULL_SLICE_CRED, os.R_OK):
#        logger.info("Creating GENI API null slice credentials.")
#        create_null_slice_cred()
        
# Request to run check_and_create_auth after syncdb
signals.post_syncdb.connect(check_and_create_auth)
