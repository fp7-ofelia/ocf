
import os
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
