#!/usr/bin/env python

import sys
import os.path
import optparse
import geniutil
import datetime

SA_CERT_FILE = 'sa-cert.pem'
SA_KEY_FILE = 'sa-key.pem'
MA_CERT_FILE = 'ma-cert.pem'
MA_KEY_FILE = 'ma-key.pem'
AM_CERT_FILE = 'am-cert.pem'
AM_KEY_FILE = 'am-key.pem'

ADMIN_NAME = 'admin'
ADMIN_EMAIL = '%s@example.net' %  (ADMIN_NAME,)
ADMIN_KEY_FILE = '%s-key.pem' %   (ADMIN_NAME,)
ADMIN_CERT_FILE = '%s-cert.pem' % (ADMIN_NAME,)
ADMIN_CRED_FILE = '%s-cred.xml' % (ADMIN_NAME,)
USER_NAME = 'alice'
USER_EMAIL = '%s@example.com' % (USER_NAME,)
USER_KEY_FILE = '%s-key.pem' % (USER_NAME,)
USER_CERT_FILE = '%s-cert.pem' % (USER_NAME,)
USER_CRED_FILE = '%s-cred.xml' % (USER_NAME,)
BAD_USER_NAME = 'malcom'
BAD_USER_EMAIL = '%s@example.org' % (BAD_USER_NAME,)
BAD_USER_KEY_FILE = '%s-key.pem' % (BAD_USER_NAME,)
BAD_USER_CERT_FILE = '%s-cert.pem' % (BAD_USER_NAME,)
BAD_USER_CRED_FILE = '%s-cred.xml' % (BAD_USER_NAME,)
SLICE_NAME = 'pizzaslice'
SLICE_CRED_FILE = 'pizzaslice_cred.xml'

CRED_EXPIRY = datetime.datetime.utcnow() + datetime.timedelta(days=100)

def write_file(dir_path, filename, str, silent=False):
    path = os.path.join(dir_path, filename)
    with open(path, 'w') as f:
        f.write(str)
    if not silent:
        print "  Wrote file %s" % (path,)

if __name__ == "__main__":
    parser = optparse.OptionParser(usage = "usage: %prog directory_path")
    parser.add_option("--silent", action="store_true", help="Silence output", default=False)
    parser.add_option("--authority", help="Authority to use (defaults to 'test.fp7:ofelia:eu)", default="test:fp7-ofelia:eu")

    opts, args = parser.parse_args(sys.argv)

    if len(args) == 1: # no args given, index 0 is the script name
        parser.print_help()
        sys.exit(0)
    
    dir_path = args[1]
    if not os.path.isdir(dir_path):
        raise ValueError("The given path does not exist.")

    if not opts.silent:
        print "Creating SA certificate"
    urn = geniutil.encode_urn(opts.authority, 'authority', 'sa')
    sa_c, sa_pu, sa_pr = geniutil.create_certificate(urn, is_ca=True)
    write_file(dir_path, SA_CERT_FILE, sa_c, opts.silent)
    write_file(dir_path, SA_KEY_FILE, sa_pr, opts.silent)
    
    if not opts.silent:
        print "Creating MA certificate"
    urn = geniutil.encode_urn(opts.authority, 'authority', 'ma')
    ma_c, ma_pu, ma_pr = geniutil.create_certificate(urn, is_ca=True)
    write_file(dir_path, MA_CERT_FILE, ma_c, opts.silent)
    write_file(dir_path, MA_KEY_FILE, ma_pr, opts.silent)
    
    if not opts.silent:
        print "Creating AM certificate"
    urn = geniutil.encode_urn(opts.authority, 'authority', 'am')
    am_c, am_pu, am_pr = geniutil.create_certificate(urn)
    write_file(dir_path, AM_CERT_FILE, am_c, opts.silent)
    write_file(dir_path, AM_KEY_FILE, am_pr, opts.silent)

    if not opts.silent:
        print "--------------------"
        print "You may want to configure the above certificates & private keys in your SA/MA/AM servers."
        print "Also, you may want to add the SA & MA certificates to the trusted_roots of the AM servers."
        print "--------------------"

    if not opts.silent:
        print "Creating test user cert and cred (valid, signed by MA)"
    urn = geniutil.encode_urn(opts.authority, 'user', USER_NAME)
    u_c,u_pu,u_pr = geniutil.create_certificate(urn, issuer_key=ma_pr, issuer_cert=ma_c, email=USER_EMAIL)
    write_file(dir_path, USER_CERT_FILE, u_c, opts.silent)
    write_file(dir_path, USER_KEY_FILE, u_pr, opts.silent)
    u_cred = geniutil.create_credential(u_c, u_c, ma_pr, ma_c, "user", CRED_EXPIRY)
    write_file(dir_path, USER_CRED_FILE, u_cred, opts.silent)


    if not opts.silent:
        print "Creating bad test user cert and cred (invalid, self-signed)"
    urn = geniutil.encode_urn(opts.authority, 'user', BAD_USER_NAME)
    bu_c,bu_pu,bu_pr = geniutil.create_certificate(urn, email=BAD_USER_EMAIL)
    write_file(dir_path, BAD_USER_CERT_FILE, bu_c, opts.silent)
    write_file(dir_path, BAD_USER_KEY_FILE, bu_pr, opts.silent)
    bu_cred = geniutil.create_credential(bu_c, bu_c, ma_pr, ma_c, "user", CRED_EXPIRY)
    write_file(dir_path, BAD_USER_CRED_FILE, bu_cred, opts.silent)
    
    if not opts.silent:
        print "Creating admin cert and cred"
    urn = geniutil.encode_urn(opts.authority, 'user', ADMIN_NAME)
    a_c,a_pu,a_pr = geniutil.create_certificate(urn, issuer_key=ma_pr, issuer_cert=ma_c, email=ADMIN_EMAIL)
    write_file(dir_path, ADMIN_CERT_FILE, a_c, opts.silent)
    write_file(dir_path, ADMIN_KEY_FILE, a_pr, opts.silent)
    a_cred = geniutil.create_credential(a_c, a_c, ma_pr, ma_c, "user", CRED_EXPIRY)
    write_file(dir_path, ADMIN_CRED_FILE, a_cred, opts.silent)

    if not opts.silent:
        print "Creating slice credential for valid test user"
    urn = geniutil.encode_urn(opts.authority, 'slice', SLICE_NAME)
    s_c = geniutil.create_slice_certificate(urn, sa_pr, sa_c, CRED_EXPIRY)
    s_cred = geniutil.create_credential(u_c, s_c, sa_pr, sa_c, "slice", CRED_EXPIRY)
    write_file(dir_path, SLICE_CRED_FILE, s_cred, opts.silent)

    if not opts.silent:
        print "--------------------"
        print "You can use the user certificates and slice cert to test. In production you may acquire them from a MA and SA."
        print "--------------------"

