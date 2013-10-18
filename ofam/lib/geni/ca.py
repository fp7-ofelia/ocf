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
'''
Sample code showing how to use openssl libraries to generate certificates.
Obsolete and unused, but useful reference code.
'''

import os.path
import subprocess

class CertificateAuthority(object):

    def __init__(self):
        pass

    def mkdir(self, dir):
        if not os.path.isdir(dir):
            os.mkdir(dir)

    def newca(self, basedir='.'):
        """Create a new CA directory structure starting at rootdir."""
        # Based on the CA script from openssl
        rootdir = os.path.join(basedir, 'demoCA')
        self.mkdir(rootdir)
        for dir in ('certs', 'crl', 'newcerts', 'private'):
            self.mkdir(os.path.join(rootdir, dir))
        # write '00' to serial file
        with open(os.path.join(rootdir, 'serial'), 'wb') as f:
            f.write('00')
        # touch index file
        open(os.path.join(rootdir, 'index.txt'), 'w').close()
        # It would be nice to configure the default values and the set
        # of values requested.
        subprocess.call(['openssl', 'req', '-new', '-keyout',
                         os.path.join(rootdir, 'private', 'cakey.pem'),
                         '-out', os.path.join(rootdir, 'careq.pem')])
        subprocess.call(['openssl', 'ca', '-out', 
                         os.path.join(rootdir, 'cacert.pem'),
                         '-days', '1095', # 3 years
                         '-batch', '-keyfile',
                         os.path.join(rootdir, 'private', 'cakey.pem'),
                         '-selfsign', '-infiles', 
                         os.path.join(rootdir, 'careq.pem')])

    def signreq(self, reqfile, certfile, basedir='.', ):
        """Signs a certificate request."""
        subprocess.call(['openssl', 'ca', '-policy', 'policy_anything',
                         '-out', certfile, '-infiles', reqfile])
