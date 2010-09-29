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

"""
Create a certificate authority and some basic certs and keys.

A CA is created, as well as certificates and keys for two authorities:
a Expedient and an aggregate manager. Finally, a user cert and
key is created for a user (named Alice by default). Options allow
controlling which certs are created.
"""

import sys

# Check python version. Requires 2.6 or greater, but less than 3.
if sys.version_info < (2, 6):
    raise Exception('Must use python 2.6 or greater.')
elif sys.version_info >= (3,):
    raise Exception('Not python 3 ready')

import optparse
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
import gcf.geni
import gcf.sfa.trust.gid as gid
import gcf.sfa.trust.certificate as cert
import gcf.sfa.trust.credential as cred

#CA_CERT_FILE = 'ca-cert.pem'
#CA_KEY_FILE = 'ca-key.pem'
#CH_CERT_FILE = 'ch-cert.pem'
#CH_KEY_FILE = 'ch-key.pem'
#AM_CERT_FILE = 'am-cert.pem'
#AM_KEY_FILE = 'am-key.pem'
CA_CERT_FILE = 'ca.crt'
CA_KEY_FILE = 'ca.key'
CH_CERT_FILE = 'ch.crt'
CH_KEY_FILE = 'ch.key'
AM_CERT_FILE = 'server.crt'
AM_KEY_FILE = 'server.key'

# Substitute eg openflow:stanford
#GPO_CA_CERT_PREFIX = "geni.net:gpo"
#GCF_CERT_PREFIX = "geni.net:gpo:gcf"
GPO_CA_CERT_PREFIX = "openflow:stanford"
GCF_CERT_PREFIX = "openflow:stanford"

USER_CERT_LIFE=3600
# See sfa/trust/rights.py
USER_CERT_PRIVS = "embed:1, bind:1"

# For the subject of user/experiments certs, eg gcf+user+<username>
USER_CERT_TYPE = 'user'
# For CHs and AMs. EG gcf+authority+am
# See sfa/util/namespace.py eg
AUTHORITY_CERT_TYPE = 'authority'
CA_CERT_SUBJ = 'ca' # Note that others might call this a SA
CH_CERT_SUBJ = 'ch'
AM_CERT_SUBJ = 'am'

# Prefix is like geni.net:gpo
# type is authority or user
# subj is sa or am or ch, or the username
def create_cert(prefix, type, subj, issuer_key=None, issuer_cert=None, intermediate=False):
    '''Create a new certificate and return it and the associated keys.
    If issure cert and key are given, they sign the certificate. Otherwise
    it is a self-signed certificate. If intermediate then mark this 
    as an intermediate CA certiciate (can sign).
    Subject of the cert is prefix+type+subj
    '''
    
    subject = "%s+%s+%s" % (prefix, type, subj)
    urn = 'urn:publicid:IDN+%s' % subject
    newgid = gid.GID(create=True, subject=subject,
                     urn=urn)
    keys = cert.Keypair(create=True)
    newgid.set_pubkey(keys)
    if intermediate:
        newgid.set_intermediate_ca(intermediate)
        
    if issuer_key:
        newgid.set_issuer(issuer_key, cert=issuer_cert)
        newgid.set_parent(issuer_cert)
    else:
        # create a self-signed cert
        newgid.set_issuer(keys, subject=subject)
    newgid.encode()
    newgid.sign()
    return newgid, keys

# unused method
def create_user_credential(user_gid, issuer_keyfile, issuer_certfile):
    ''' Given user GID andd CH cert and key, create a user credential.'''
    ucred = cred.Credential()
    ucred.set_gid_caller(user_gid)
    ucred.set_gid_object(user_gid)
    ucred.set_lifetime(USER_CERT_LIFE)
    ucred.set_privileges(USER_CERT_PRIVS)
    ucred.encode()
    ucred.set_issuer_keys(issuer_keyfile, issuer_certfile)
    ucred.sign()
    return ucred

def make_ca_cert(dir):
    '''Create the CA cert and save it to given dir and return them'''
    (ca_cert, ca_key) = create_cert(GPO_CA_CERT_PREFIX,AUTHORITY_CERT_TYPE,CA_CERT_SUBJ)
    ca_cert.save_to_file(os.path.join(dir, CA_CERT_FILE))
    ca_key.save_to_file(os.path.join(dir, CA_KEY_FILE))
    print "Created CA Cert/keys in %s/%s and %s" % (dir, CA_CERT_FILE, CA_KEY_FILE)
    return (ca_cert, ca_key)

def make_ch_cert(dir, ca_cert, ca_key):
    '''Make a cert for Expedient signed by given CA saved to 
    given directory and returned.'''
    (ch_gid, ch_keys) = create_cert(GCF_CERT_PREFIX, AUTHORITY_CERT_TYPE,CH_CERT_SUBJ, ca_key, ca_cert, True)
    ch_gid.save_to_file(os.path.join(dir, CH_CERT_FILE))
    ch_keys.save_to_file(os.path.join(dir, CH_KEY_FILE))
    print "Created CH cert/keys in %s/%s and %s" % (dir, CH_CERT_FILE, CH_KEY_FILE)
    return (ch_keys, ch_gid)

def make_am_cert(dir, ca_cert, ca_key):
    '''Make a cert for the aggregate manager signed by given CA cert/key
    and saved in given dir. NOT RETURNED.'''
    (am_gid, am_keys) = create_cert(GCF_CERT_PREFIX, AUTHORITY_CERT_TYPE,AM_CERT_SUBJ, ca_key, ca_cert, True)
    am_gid.save_to_file(os.path.join(dir, AM_CERT_FILE))
    am_keys.save_to_file(os.path.join(dir, AM_KEY_FILE))
    print "Created AM cert/keys in %s/%s and %s" % (dir, AM_CERT_FILE, AM_KEY_FILE)

def make_user_cert(dir, username, ch_keys, ch_gid):
    '''Make a GID/Cert for given username signed by given CH GID/keys, 
    saved in given directory. Not returned.'''
    (alice_gid, alice_keys) = create_cert(GCF_CERT_PREFIX,USER_CERT_TYPE,username, ch_keys, ch_gid)
    alice_gid.save_to_file(os.path.join(dir, ('%s.crt' % username)))
    alice_keys.save_to_file(os.path.join(dir, ('%s.key' % username)))
# Make a Credential for Alice
#alice_cred = create_user_credential(alice_gid, CH_KEY_FILE, CH_CERT_FILE)
#alice_cred.save_to_file('../alice-user-cred.xml')
    print "Created Experimenter %s cert/keys in %s" % (username, dir)

def parse_args(argv):
    parser = optparse.OptionParser()
    parser.add_option("-d", "--directory", default='.',
                      help="directory for created cert files", metavar="DIR")
    parser.add_option("-u", "--username", default='experimenter',
                      help="Experimenter username")
    parser.add_option("--notAll", action="store_true", default=True,
                      help="Do NOT create all cert/keys: Supply other options to generate particular certs.")
    parser.add_option("--ca", action="store_true", default=False,
                      help="Create CA cert/keys")
    parser.add_option("--ch", action="store_true", default=False,
                      help="Create CH cert/keys")
    parser.add_option("--am", action="store_true", default=False,
                      help="Create AM cert/keys")
    parser.add_option("--exp", action="store_true", default=False,
                      help="Create experimenter cert/keys")
    return parser.parse_args()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts, args = parse_args(argv)
    username = "alice"
    if opts.username:
        username = opts.username
    dir = "."
    if opts.directory:
        dir = opts.directory

    ca_cert = None
    ca_key = None
    if not opts.notAll or opts.ca:
        (ca_cert, ca_key) = make_ca_cert(dir)
    else:
        if not opts.notAll or opts.ch or opts.am:
            try:
                ca_cert = gid.GID(filename=os.path.join(dir,CA_CERT_FILE))
                ca_key = cert.Keypair(filename=os.path.join(dir,CA_KEY_FILE))
            except Exception, exc:
                sys.exit("Failed to read CA Cert/key from %s/%s and %s: %s" % (dir, CA_CERT_FILE, CA_KEY_FILE, exc))

    ch_keys = None
    ch_gid = None
    if not opts.notAll or opts.ch:
        (ch_keys, ch_gid) = make_ch_cert(dir, ca_cert, ca_key)
    else:
        if not opts.notAll or opts.exp:
            try:
                ch_gid = gid.GID(filename=os.path.join(dir,CH_CERT_FILE))
                ch_keys = cert.Keypair(filename=os.path.join(dir,CH_KEY_FILE))
            except Exception, exc:
                sys.exit("Failed to read CH cert/key from %s/%s and %s: %s" % (dir, CHCERT_FILE, CH_KEY_FILE, exc))

    if not opts.notAll or opts.am:
        make_am_cert(dir, ca_cert, ca_key)

    if not opts.notAll or opts.exp:
        make_user_cert(dir, username, ch_keys, ch_gid)

    return 0

if __name__ == "__main__":
    sys.exit(main())
