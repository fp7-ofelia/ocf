#!/usr/bin/python
#
### $Id: sfa-server.py 15186 2009-09-30 23:20:21Z bakers $
### $URL: http://svn.planet-lab.org/svn/sfa/trunk/sfa/server/sfa-server.py $
#
# GENI PLC Wrapper
#
# This wrapper implements the Geni Registry and Slice Interfaces on PLC.
# Depending on command line options, it starts some combination of a
# Registry, an Aggregate Manager, and a Slice Manager.
#
# There are several items that need to be done before starting the wrapper
# server.
#
# NOTE:  Many configuration settings, including the PLC maintenance account
# credentials, URI of the PLCAPI, and PLC DB URI and admin credentials are initialized
# from your MyPLC configuration (/etc/planetlab/plc_config*).  Please make sure this information
# is up to date and accurate.
#
# 1) Import the existing planetlab database, creating the
#    appropriate geni records. This is done by running the "sfa-import-plc.py" tool.
#
# 2) Create a "trusted_roots" directory and place the certificate of the root
#    authority in that directory. Given the defaults in sfa-import-plc.py, this
#    certificate would be named "planetlab.gid". For example,
#
#    mkdir trusted_roots; cp authorities/planetlab.gid trusted_roots/
#
# TODO: Can all three servers use the same "registry" certificate?
##

# TCP ports for the three servers
registry_port=12345
aggregate_port=12346
slicemgr_port=12347

import os, os.path
from optparse import OptionParser

from sfa.trust.trustedroot import TrustedRootList
from sfa.trust.certificate import Keypair, Certificate

from sfa.server.registry import Registry
from sfa.server.aggregate import Aggregate
from sfa.server.slicemgr import SliceMgr

from sfa.trust.hierarchy import Hierarchy

from sfa.util.config import Config

# after http://www.erlenstar.demon.co.uk/unix/faq_2.html
def daemon():
    """Daemonize the current process."""
    if os.fork() != 0: os._exit(0)
    os.setsid()
    if os.fork() != 0: os._exit(0)
    os.umask(0)
    devnull = os.open(os.devnull, os.O_RDWR)
    os.dup2(devnull, 0)
    # xxx fixme - this is just to make sure that nothing gets stupidly lost - should use devnull
    crashlog = os.open('/var/log/sfa.daemon', os.O_RDWR | os.O_APPEND | os.O_CREAT, 0644)
    os.dup2(crashlog, 1)
    os.dup2(crashlog, 2)

def main():
    # xxx get rid of globals - name consistently CamelCase or under_score
    global AuthHierarchy
    global TrustedRoots
    global registry_port
    global aggregate_port
    global slicemgr_port

    # Generate command line parser
    parser = OptionParser(usage="plc [options]")
    parser.add_option("-r", "--registry", dest="registry", action="store_true",
         help="run registry server", default=False)
    parser.add_option("-s", "--slicemgr", dest="sm", action="store_true",
         help="run slice manager", default=False)
    parser.add_option("-a", "--aggregate", dest="am", action="store_true",
         help="run aggregate manager", default=False)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", 
         help="verbose mode", default=False)
    parser.add_option("-d", "--daemon", dest="daemon", action="store_true",
         help="Run as daemon.", default=False)
    (options, args) = parser.parse_args()

    hierarchy = Hierarchy()
    path = hierarchy.basedir
    key_file = os.path.join(path, "server.key")
    cert_file = os.path.join(path, "server.cert")
    
    if (options.daemon):  daemon()

    if (os.path.exists(key_file)) and (not os.path.exists(cert_file)):
        # If private key exists and cert doesnt, recreate cert
        key = Keypair(filename=key_file)
        cert = Certificate(subject="registry")
        cert.set_issuer(key=key, subject="registry")
        cert.set_pubkey(key)
        cert.sign()
        cert.save_to_file(cert_file)

    elif (not os.path.exists(key_file)) or (not os.path.exists(cert_file)):
        # if no key is specified, then make one up
        key = Keypair(create=True)
        key.save_to_file(key_file)
        cert = Certificate(subject="registry")
        cert.set_issuer(key=key, subject="registry")
        cert.set_pubkey(key)
        cert.sign()
        cert.save_to_file(cert_file)

    AuthHierarchy = Hierarchy()

    TrustedRoots = TrustedRootList(Config().get_trustedroots_dir())

    # start registry server
    if (options.registry):
        r = Registry("", registry_port, key_file, cert_file)
        #r.trusted_cert_list = TrustedRoots.get_list()
        #r.hierarchy = AuthHierarchy
        r.start()

    # start aggregate manager
    if (options.am):
        a = Aggregate("", aggregate_port, key_file, cert_file)
        #a.trusted_cert_list = TrustedRoots.get_list()
        a.start()

    # start slice manager
    if (options.sm):
        s = SliceMgr("", slicemgr_port, key_file, cert_file)
        #s.trusted_cert_list = TrustedRoots.get_list()
        s.start()

if __name__ == "__main__":
    main()
