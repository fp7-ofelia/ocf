#----------------------------------------------------------------------
# Copyright (c) 2011-2012 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
#----------------------------------------------------------------------
'''
Certificate (GID in SFA terms) creation and verification utilities.
'''


from sfa.trust.gid import GID
from sfa.trust.certificate import Keypair
from geni.util.urn_util import URN

def create_cert(urn, issuer_key=None, issuer_cert=None, ca=False,
                public_key=None, lifeDays=1825, email=None):
    '''Create a new certificate and return it and the associated keys.
    If issuer cert and key are given, they sign the certificate. Otherwise
    it is a self-signed certificate. 
    
    If ca then mark this as a CA certificate (can sign other certs).
    
    lifeDays is the lifetime of the supplied cert - default is 1825 (5 years).

    Certificate URN must be supplied.
    CN of the cert will be dotted notation authority.type.name from the URN.
    '''
    # Note the below throws a ValueError if it wasnt a valid URN
    c_urn = URN(urn=urn)
    dotted = '%s.%s.%s' % (c_urn.getAuthority(), c_urn.getType(), c_urn.getName())

    subject = dict()
    subject['CN'] = dotted[:64]
    if email:
        subject['emailAddress'] = email
    newgid = GID(create=True, subject=subject, urn=urn, lifeDays=lifeDays)
    
    if public_key is None:
        # create a new key pair
        keys = Keypair(create=True)
    else:
        # use the specified public key file
        keys = Keypair()
        keys.load_pubkey_from_file(public_key)
    newgid.set_pubkey(keys)
    newgid.set_is_ca(ca)

    if issuer_key and issuer_cert:
        # the given issuer will issue this cert
        if isinstance(issuer_key,str):
            issuer_key = Keypair(filename=issuer_key)
        if isinstance(issuer_cert,str):
            issuer_cert = GID(filename=issuer_cert)
        newgid.set_issuer(issuer_key, cert=issuer_cert)
        newgid.set_parent(issuer_cert)
    else:
        # create a self-signed cert
        newgid.set_issuer(keys, subject=dotted)

    newgid.encode()
    newgid.sign()
    return newgid, keys
