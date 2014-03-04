import tempfile
import uuid
import os

from ext.geni.util.urn_util import URN
from ext.sfa.trust.gid import GID
# import ext.geni
from ext.sfa.trust.certificate import Keypair
from ext.geni.util import cert_util as gcf_cert_util
import ext.sfa.trust.credential as sfa_cred
import ext.sfa.trust.rights as sfa_rights

def decode_urn(urn):
    """Returns authority, type and name associated with the URN as string.
    example call:
      authority, typ, name = decode_urn("urn:publicid:IDN+eict.de+user+motine")
    """
    urn = URN(urn=str(urn))
    return urn.getAuthority(), urn.getType(), urn.getName() 

def encode_urn(authority, typ, name):
    """
    Returns a URN string with the given {authority}, {typ}e and {name}.
    {typ} shall be either of the following: authority, slice, user, sliver, (project or meybe others: http://groups.geni.net/geni/wiki/GeniApiIdentifiers#Type)
    example call:
      urn_str = encode_urn("eict.de", "user", "motine")
    """
    return URN(authority=authority, type=typ, name=name).urn_string()

def create_certificate(urn, issuer_key=None, issuer_cert=None, is_ca=False,
                       public_key=None, life_days=1825, email=None, uuidarg=None):
    """Creates a certificate.
    {issuer_key} private key of the issuer. can either be a string in pem format or None.
    {issuer_cert} can either be a string in pem format or None.
    If either {issuer_cert} or {issuer_key} is None, the cert becomes self-signed
    {public_key} contains the pub key which will be embedded in the certificate. If None a new key is created, otherwise it must be a string)
    {uuidarg} can be a uuid.UUID or a string.
    
    Returns tuple in the following order:
      x509 certificate in PEM format
      public key of the keypair related to the new certificate in PEM format
      public key of the keypair related to the new certificate in PEM format or None if the the {public_key} was given.
    
    IMPORTANT
    Do not add an email when creating sa/ma/cm. This may lead to unverificable certs later.
    """
    # create temporary files for some params, because gcf's create_cert works with files and I did not want to duplicate the code
    pub_key_param = None
    if public_key:
        fh, pub_key_param = tempfile.mkstemp(); os.write(fh, public_key); os.close(fh)
    issuer_key_param, issuer_cert_param = None, None
    if issuer_key and issuer_cert:
        fh, issuer_key_param = tempfile.mkstemp(); os.write(fh, issuer_key); os.close(fh)
        fh, issuer_cert_param = tempfile.mkstemp(); os.write(fh, issuer_cert); os.close(fh)

    cert_gid, cert_keys = gcf_cert_util.create_cert(urn, issuer_key_param, issuer_cert_param, is_ca, pub_key_param, life_days, email, uuidarg)
    if pub_key_param:
        os.remove(pub_key_param)
    if issuer_key_param:
        os.remove(issuer_key_param)
    if issuer_cert_param:
        os.remove(issuer_cert_param)
    
    priv_key_result = None
    if not public_key:
        priv_key_result = cert_keys.as_pem()
    return cert_gid.save_to_string(), cert_keys.get_m2_pkey().get_rsa().as_pem(), priv_key_result

def create_slice_certificate(slice_urn, issuer_key, issuer_cert, expiration):
    """Returns only the x509 certificate as string (as PEM)."""
    return create_certificate(slice_urn, issuer_key, issuer_cert, uuidarg=uuid.uuid4())[0]

def create_credential(owner_cert, target_cert, issuer_key, issuer_cert, typ, expiration, delegatable=False):
    """
    {expiration} can be a datetime.datetime or a int/float (see http://docs.python.org/2/library/datetime.html#datetime.date.fromtimestamp) or a string with a UTC timestamp in it
    {typ} is used to determine the rights (via ext/sfa/truse/rights.py) can either of the following: "user", "sa", "ma", "cm", "sm", "authority", "slice", "component" also you may specify "admin" for all privileges.
    Returns the credential as String
    """
    ucred = sfa_cred.Credential()
    ucred.set_gid_caller(GID(string=owner_cert))
    ucred.set_gid_object(GID(string=target_cert))
    ucred.set_expiration(expiration)

    if typ == "admin":
        if delegatable:
            raise ValueError("Admin credentials can not be delegatable")
        privileges = sfa_rights.Rights("*")
    else:
        privileges = sfa_rights.determine_rights(typ, None)
        privileges.delegate_all_privileges(delegatable)
    ucred.set_privileges(privileges)
    ucred.encode()

    issuer_key_file, issuer_key_filename = tempfile.mkstemp(); os.write(issuer_key_file, issuer_key); os.close(issuer_key_file)
    issuer_cert_file, issuer_cert_filename = tempfile.mkstemp(); os.write(issuer_cert_file, issuer_cert); os.close(issuer_cert_file)

    ucred.set_issuer_keys(issuer_key_filename, issuer_cert_filename) # priv, gid
    ucred.sign()

    os.remove(issuer_key_filename)
    os.remove(issuer_cert_filename)

    return ucred.save_to_string()