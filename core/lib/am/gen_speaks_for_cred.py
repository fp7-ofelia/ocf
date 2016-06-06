import sys
import os
import glob
from credentials.src.trustgcf.speaksfor_util import create_sign_abaccred
from credentials.src.trustgcf.gid import GID


dir_path = 'deploy/trusted/certs/'
cbas_cert_path = 'deploy/trusted/certs/ca-cert.pem'
cbas_key_path = 'deploy/trusted/cert_keys/ca-key.pem'


def create_credentials(output_file_name, issuer_cert,
                       issuer_key, target_cert, role=None):

    if not os.path.isfile(issuer_cert):
        print "Could not load certificate file: "+issuer_cert
        sys.exit(1)
    if not os.path.isfile(issuer_key):
        print "Could not load key file: "+issuer_key
        sys.exit(1)
    if not os.path.isfile(target_cert):
        print "Could not load certificate file: "+target_cert
        sys.exit(1)

    issuer_gid = GID(filename=issuer_cert)
    target_gid = GID(filename=target_cert)

    if not role:
        role_head = "Trusted"
        role_tail = None
    elif role == 'speaks_for':
        role_head = None
        role_tail = "Trusted"
    elif role == 'Trusted':
        role_head = "Trusted"
        role_tail = "Trusted"
    else:
        print 'Unrecognized role. Aborting...'
        sys.exit(1)

    create_sign_abaccred(target_gid, issuer_gid, None,
                         issuer_key, output_file_name + "-speaks_for.xml",
                         dur_days=365*10, role_head=role_head,
                         role_tail=role_tail)

if __name__ == "__main__":

    cbas_install_dir = raw_input("Enter absolute path to CBAS \
        directory (e.g., /opt/felix/cbas):")

    if not os.path.exists(cbas_install_dir):
            print 'The provided path does not exist: '+cbas_install_dir
            print 'aborting...'
            sys.exit(1)
    else:
        dir_path = os.path.join(cbas_install_dir, dir_path)
        cbas_cert_path = os.path.join(cbas_install_dir, cbas_cert_path)
        cbas_key_path = os.path.join(cbas_install_dir, cbas_key_path)

    print ""
    print "1. Issue speaks_for credential to a user"
    print "2. Issue speaks_for credential to an RO"
    print "3. Acting as a non-master island, issue speaks_for \
        credential to master island"
    print "4. Acting as a master island, issue speaks_for \
        credential to peer islands"

    op = input("Select mode of operation (1-4): ")

    if op == 4:
        print "Creating speaks_for credentials for all trusted islands..."
        cert_list = glob.glob(dir_path+'*+ca-cert.pem')
        for cert_path in cert_list:
            output_file = cert_path[len(dir_path):cert_path.find('+')]
            create_credentials(output_file, cbas_cert_path,
                               cbas_key_path, cert_path, 'Trusted')

    elif op == 3:
        input_str = raw_input("Enter master cbas name (e.g., \
            mcbas.i2cat.net):").strip()
        mcbas_cert_path = dir_path+input_str+'+authority+ca-cert.pem'
        if not os.path.isfile(mcbas_cert_path):
            print 'certificate for provided name does \
                not exist under ' + dir_path
            print 'aborting...'
            sys.exit(1)
        else:
            create_credentials(input_str, cbas_cert_path, cbas_key_path,
                               mcbas_cert_path, 'Trusted')

    elif op == 1:
        cert_file = raw_input("Enter user cert file: ").strip()
        if not os.path.isfile(cert_file):
            print 'given certificate file does not exist'
            print 'aborting...'
            sys.exit(1)
        key_file = cert_file.replace('-cert', '-key')
        if not os.path.isfile(key_file) or key_file == cert_file:
            key_file = raw_input("Enter user cert key file: ")
            if not os.path.isfile(key_file):
                print 'given certificate key file does not exist'
                print 'aborting...'
                sys.exit(1)

        output_file = cert_file[cert_file.rfind('/')+1:cert_file.find('-cert')] \
            if cert_file.find('-cert') > 0 else 'output'
        create_credentials(output_file, cert_file, key_file,
                           cbas_cert_path, 'speaks_for')

    elif op == 2:
        cert_file = raw_input("Enter RO cert file: ").strip()
        if not os.path.isfile(cert_file):
            print 'given certificate file does not exist'
            print 'aborting...'
            sys.exit(1)

        output_file = cert_file[cert_file.rfind('/')+1:cert_file.find('-cert')] \
            if cert_file.find('-cert') > 0 else 'output'
        create_credentials(output_file, cbas_cert_path, cbas_key_path,
                           cert_file)
    else:
        print 'Entered invalid option. Aborting...'
