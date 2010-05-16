#!/usr/bin/env python

#----------------------------------------------------------------------
# Copyright (c) 2010 Raytheon BBN Technologies
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

"""Create a certificate authority and some basic certs and keys.

A CA is created, as well as certificates and keys for two authorities:
a clearinghouse and an aggregate manager. Finally, a user cert and
key is created for a user named Alice.
"""

import optparse
import os.path
import sys
import geni
import sfa.trust.gid as gid
import sfa.trust.certificate as cert
import sfa.trust.credential as cred

CA_CERT_FILE = 'ca.crt'
CA_KEY_FILE = 'ca.key'
CH_CERT_FILE = 'ch.crt'
CH_KEY_FILE = 'ch.key'
AM_CERT_FILE = 'server.crt'
AM_KEY_FILE = 'server.key'

def create_cert(subject, type, issuer_key=None, issuer_cert=None):
    publicid = 'IDN openflow//stanford %s %s' % (type, subject)
    urn = geni.publicid_to_urn(publicid)
    newgid = gid.GID(create=True, subject=subject, uuid=gid.create_uuid(),
                     urn=urn)
    keys = cert.Keypair(create=True)
    newgid.set_pubkey(keys)
    if issuer_key:
        newgid.set_issuer(issuer_key, cert=issuer_cert)
    else:
        # create a self-signed cert
        if isinstance(subject, dict):
            name = subject["CN"]
        else:
            name = subject
        newgid.set_issuer(keys, subject=name)
    newgid.encode()
    newgid.sign()
    return newgid, keys

def create_user_credential(user_gid, issuer_keyfile, issuer_certfile):
    ucred = cred.Credential()
    ucred.set_gid_caller(user_gid)
    ucred.set_gid_object(user_gid)
    ucred.set_lifetime(3600)
    ucred.set_privileges("embed:1, bind:1")
    ucred.encode()
    ucred.set_issuer_keys(issuer_keyfile, issuer_certfile)
    ucred.sign()
    return ucred

def get_subject(type):
    import socket
    return type
#    return dict(
#        CN=socket.getfqdn(),
#        C="XY",
#        ST="Unknown",
#        L="Unknown",
#        O="openSuSE Linux Web Server",
#        OU="web server",
#    )

def make_ca_certs(dir):
    # Create the CA cert
    (ca_cert, ca_key) = create_cert(get_subject("ca"), 'authority')
    ca_cert.save_to_file(os.path.join(dir, CA_CERT_FILE))
    ca_key.save_to_file(os.path.join(dir, CA_KEY_FILE))

def make_ch_certs(dir):
    # Make a cert for the clearinghouse
    ca_cert = gid.GID(filename=os.path.join(dir,CA_CERT_FILE))
    ca_key = cert.Keypair(filename=os.path.join(dir,CA_KEY_FILE))
    (ch_gid, ch_keys) = create_cert(get_subject("ch"), 'authority', ca_key, ca_cert)
    ch_gid.save_to_file(os.path.join(dir, CH_CERT_FILE))
    ch_keys.save_to_file(os.path.join(dir, CH_KEY_FILE))

def make_am_certs(dir):        
    # Make a cert for the aggregate manager
    ca_cert = gid.GID(filename=os.path.join(dir,CA_CERT_FILE))
    ca_key = cert.Keypair(filename=os.path.join(dir,CA_KEY_FILE))
    (am_gid, am_keys) = create_cert(get_subject("am"), 'authority', ca_key, ca_cert)
    am_gid.save_to_file(os.path.join(dir, AM_CERT_FILE))
    am_keys.save_to_file(os.path.join(dir, AM_KEY_FILE))

def make_exp_certs(dir):
    # Make a GID/Cert for Alice
    ca_cert = gid.GID(filename=os.path.join(dir,CA_CERT_FILE))
    ca_key = cert.Keypair(filename=os.path.join(dir,CA_KEY_FILE))
    (alice_gid, alice_keys) = create_cert('experimenter', 'user', ca_key, ca_cert)
    alice_gid.save_to_file(os.path.join(dir, 'experimenter.crt'))
    alice_keys.save_to_file(os.path.join(dir, 'experimenter.key'))
    
def make_certs(dir):
    make_ca_certs(dir)
    make_ch_certs(dir)
    make_am_certs(dir)
    make_exp_certs(dir)
    
# Make a Credential for Alice
#alice_cred = create_user_credential(alice_gid, CH_KEY_FILE, CH_CERT_FILE)
#alice_cred.save_to_file('../alice-user-cred.xml')

def parse_args(argv):
    parser = optparse.OptionParser()
    parser.add_option("-d", "--directory", default='.',
                      help="directory for created cert files", metavar="DIR")
    parser.add_option("--am", action="store_true", default=False,
                      help="Create AM cert/keys")
    parser.add_option("--ch", action="store_true", default=False,
                      help="Create CH cert/keys")
    parser.add_option("--ca", action="store_true", default=False,
                      help="Create CA cert/keys")
    parser.add_option("--exp", action="store_true", default=False,
                      help="Create experimenter cert/keys")
    return parser.parse_args()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts, args = parse_args(argv)
    if opts.directory:
        if opts.ca:
            make_ca_certs(opts.directory)
        if opts.ch:
            make_ch_certs(opts.directory)
        if opts.exp:
            make_exp_certs(opts.directory)
        if opts.am:
            make_am_certs(opts.directory)
    return 0

if __name__ == "__main__":
    sys.exit(main())
