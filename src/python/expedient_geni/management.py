'''
Created on Jul 10, 2010

@author: jnaous
'''
from django.conf import settings
import os
import logging
from django.db.models import signals
import uuid

SLICE_GID_SUBJ = "gcf.slice"
SLICE_CRED_LIFETIME = 360000000

logger = logging.getLogger("geni-syncdb")

def create_expedient_certs():
    """
    Create the expedient certificate and keys for use in GENI API.
    """
    # workaround the '-' in the filename :(
    gcf = __import__("gcf.init-ca")
    initca = getattr(gcf, "init-ca")

    ca_cert, ca_key = initca.create_cert(
        settings.GCF_URN_PREFIX,
        initca.AUTHORITY_CERT_TYPE,
        initca.CA_CERT_SUBJ)
    
    ch_cert, ch_key = initca.create_cert(
        settings.GCF_URN_PREFIX,
        initca.AUTHORITY_CERT_TYPE,
        initca.CH_CERT_SUBJ,
        ca_key, ca_cert, True)
    
    ca_cert.save_to_file(settings.GCF_X509_CA_CERT)
    ca_key.save_to_file(settings.GCF_X509_CA_KEY)
    
    ch_cert.save_to_file(settings.GCF_X509_CH_CERT)
    ch_key.save_to_file(settings.GCF_X509_CH_KEY)

def create_slice_urn():
    """
    Get a new URN for a slice.
    
    @return: urn
    @rtype: string
    """
    # TODO: Currently GCF uses the URN as the slice name for 
    # MyPLC which has to be < 50 bytes.
    uuid_str = str(uuid.uuid4())[0:7]
    urn = "urn:publicid:IDN+%s+slice+%s" % (
        settings.GCF_URN_PREFIX, uuid_str)
    return urn

def create_slice_gid(slice_urn):
    """
    Create a gid for a slice and return it and its key.
    
    @param slice_urn: urn for which to create a gid
    @type slice_urn: string
    
    @return: new Slice GID and Slice key.
    @rtype: (C{gcf.sfa.trust.gid.GID} instance, C{gcf.sfa.trust.certificate.Keypair} instance)
    """
    from gcf.sfa.trust import gid, certificate
    
    newgid = gid.GID(
        create=True, subject=SLICE_GID_SUBJ,
        uuid=gid.create_uuid(), urn=slice_urn)
    keys = certificate.Keypair(create=True)
    newgid.set_pubkey(keys)
    issuer_key = certificate.Keypair(filename=settings.GCF_X509_CH_KEY)
    issuer_cert = gid.GID(filename=settings.GCF_X509_CH_CERT)
    newgid.set_issuer(issuer_key, cert=issuer_cert)
    newgid.set_parent(issuer_cert)
    newgid.encode()
    newgid.sign()
    return newgid, keys
    
def create_slice_credential(user_gid, slice_gid):
    """
    Create credentials for the slice for user_gid to use.
    
    @param user_gid: The certificate of the user.
    @type user_gid: C{gcf.sfa.trust.gid.GID} instance
    @param slice_gid: the certificate of the slice.
    @return slice_gid: C{gcf.sfa.trust.gid.GID} instance
    """
    from gcf.sfa.trust import credential, rights
    
    ucred = credential.Credential()
    ucred.set_gid_caller(user_gid)
    ucred.set_gid_object(slice_gid)
    ucred.set_lifetime(SLICE_CRED_LIFETIME)
    privileges = rights.determine_rights('slice', None)
    ucred.set_privileges(privileges)
    ucred.encode()
    ucred.set_issuer_keys(settings.GCF_X509_CH_KEY, settings.GCF_X509_CH_CERT)
    ucred.sign()
    return ucred

def create_null_slice_cred():
    """
    Create credentials for a null slice so that Expedient can call
    ListResources.
    """
    from gcf.sfa.trust import gid
    
    slice_urn = create_slice_urn()
    slice_gid, slice_keys = create_slice_gid(slice_urn)
    user_gid = gid.GID(filename=settings.GCF_X509_CH_CERT)
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
    if not os.access(settings.GCF_X509_CH_CERT, os.R_OK) or\
    not os.access(settings.GCF_X509_CH_KEY, os.R_OK):
        logger.info("Creating GENI API certificate and key.")
        _mkdirs(settings.GCF_X509_CERT_DIR)
        _mkdirs(settings.GCF_X509_KEY_DIR)
        create_expedient_certs()
    
    if not os.access(settings.GCF_NULL_SLICE_CRED, os.R_OK):
        logger.info("Creating GENI API null slice credentials.")
        _mkdirs(settings.GCF_X509_CRED_DIR)
        create_null_slice_cred()
        

# Request to run check_and_create_auth after syncdb
signals.post_syncdb.connect(check_and_create_auth)
