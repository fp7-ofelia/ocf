#!/usr/bin/python

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

import sys

# Check python version. Requires 2.6 or greater, but less than 3.
if sys.version_info < (2, 6):
    raise Exception('Must use python 2.6 or greater.')
elif sys.version_info >= (3,):
    raise Exception('Not python 3 ready')

import datetime
import logging
import optparse
import xmlrpclib
import geni
import sfa.trust.credential as cred
import sfa.trust.gid as gid

class CredentialVerifier(object):
    
    def __init__(self, root_cert_file):
        self.root_cert_files = [root_cert_file]

    def verify_from_strings(self, gid_string, cred_strings, target_urn,
                            privileges):
        def make_cred(cred_string):
            return cred.Credential(string=cred_string)
        return self.verify(gid.GID(string=gid_string),
                           map(make_cred, cred_strings),
                           target_urn,
                           privileges)
        
    def verify_source(self, source_gid, credential):
        source_urn = source_gid.get_urn()
        cred_source_urn = credential.get_gid_caller().get_urn()
        logging.debug('Verifying source %r against credential %r source %r',
                      source_urn, credential, cred_source_urn)
        result = (cred_source_urn == source_urn)
        if result:
            logging.debug('Source URNs match')
        else:
            logging.debug('Source URNs do not match')
        return result
    
    def verify_target(self, target_urn, credential):
        if not target_urn:
            logging.debug('No target specified, considering it a match.')
            return True
        else:
            cred_target_urn = credential.get_gid_object().get_urn()
            logging.debug('Verifying target %r against credential target %r',
                          target_urn, cred_target_urn)
            result = target_urn == cred_target_urn
            if result:
                logging.debug('Target URNs match.')
            else:
                logging.debug('Target URNs do not match.')
            return result

    def verify_privileges(self, privileges, credential):
        result = True
        privs = credential.get_privileges()
        for priv in privileges:
            if not privs.can_perform(priv):
                logging.debug('Privilege %s not found', priv)
                result = False
        return result

    def verify(self, gid, credentials, target_urn, privileges):
        logging.debug('Verifying privileges')
        result = list()
        for cred in credentials:
            if (self.verify_source(gid, cred) and
                self.verify_target(target_urn, cred) and
                self.verify_privileges(privileges, cred) and
                cred.verify(self.root_cert_files)):
                result.append(cred)
        if result:
            return result
        else:
            # We did not find any credential with sufficient privileges
            # Raise an exception.
            fault_code = 'Insufficient privileges'
            fault_string = 'No credential was found with appropriate privileges.'
            raise xmlrpclib.Fault(fault_code, fault_string)

class AggregateManager(object):
    
    def __init__(self, root_cert, proxy_url):
        self._cred_verifier = CredentialVerifier(root_cert)
        self.max_lease = datetime.timedelta(days=365)
        self.proxy = xmlrpclib.ServerProxy(proxy_url, xmlrpclib.SafeTransport())

    def GetVersion(self):
        return self.proxy.GetVersion()

    def ListResources(self, credentials, options):
        print 'ListResources(%r)' % (options)
        privileges = ('listresources',)
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                credentials,
                                                None,
                                                privileges)
        retval = self.proxy.ListResources(credentials, options)
        return retval
    
    def CreateSliver(self, slice_urn, credentials, rspec):
        print 'CreateSliver(%r)' % (slice_urn)
        privileges = ('createsliver',)
        creds = self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                        credentials,
                                                        slice_urn,
                                                        privileges)
        return self.proxy.CreateSliver(slice_urn, credentials, rspec)

    def DeleteSliver(self, slice_urn, credentials):
        print 'DeleteSliver(%r)' % (slice_urn)
        privileges = ('deleteslice',)
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                credentials,
                                                slice_urn,
                                                privileges)
        return self.proxy.DeleteSliver(slice_urn, credentials)
    
    def SliverStatus(self, slice_urn, credentials):
        print 'SliverStatus(%r)' % (slice_urn)
        privileges = ('getsliceresources',)
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                credentials,
                                                slice_urn,
                                                privileges)
        return self.proxy.SliverStatus()
    
    def RenewSliver(self, slice_urn, credentials, expiration_time):
        print 'RenewSliver(%r, %r)' % (slice_urn, expiration_time)
        privileges = ('renewsliver',)
        creds = self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                        credentials,
                                                        slice_urn,
                                                        privileges)
        return self.proxy.RenewSliver(slice_urn, credentials, expiration_time)
    
    def Shutdown(self, slice_urn, credentials):
        print 'Shutdown(%r)' % (slice_urn)
        return self.proxy.ShutDown(slice_urn, credentials)

def parse_args(argv):
    import socket
    parser = optparse.OptionParser()
    parser.add_option("-k", "--keyfile",
                      help="key file name", metavar="FILE")
    parser.add_option("-c", "--certfile",
                      help="certificate file name", metavar="FILE")
    parser.add_option("-r", "--rootcafile",
                      help="root ca certificate file name", metavar="FILE")
    # Could try to determine the real IP Address instead of the loopback
    # using socket.gethostbyname(socket.gethostname())
    parser.add_option("-u", "--url",
                      default="https://%s/openflow/gapi/" % socket.getfqdn(),
                      help="URL to AM server.", metavar="URL")
    parser.add_option("-H", "--host", default='127.0.0.1',
                      help="server ip", metavar="HOST")
    parser.add_option("-p", "--port", type=int, default=8001,
                      help="server port", metavar="PORT")
    parser.add_option("--debug", action="store_true", default=False,
                       help="enable debugging output")
    return parser.parse_args()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts = parse_args(argv)[0]
    level = logging.INFO
    logging.basicConfig(level=level)
    if opts.debug:
        level = logging.DEBUG
    logger = logging.Logger("am")
    logger.setLevel(level)
    delegate = AggregateManager(opts.rootcafile, opts.url)
    ams = geni.AggregateManagerServer((opts.host, opts.port),
                                      delegate=delegate,
                                      keyfile=opts.keyfile,
                                      certfile=opts.certfile,
                                      ca_certs=opts.rootcafile)
    print 'Listening on port %d...' % (opts.port)
    ams.serve_forever()

if __name__ == "__main__":
    sys.exit(main())
