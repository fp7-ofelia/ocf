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
"""
Framework to run a GENI Aggregate Manager. See geni/am 
"""

import sys
from os import path
sys.path.append(path.join(path.dirname(__file__), "../"))

# Check python version. Requires 2.6 or greater, but less than 3.
if sys.version_info < (2, 6):
    raise Exception('Must use python 2.6 or greater.')
elif sys.version_info >= (3,):
    raise Exception('Not python 3 ready')

import datetime
import logging
import optparse
import os
import xmlrpclib
import geni
from geni import CredentialVerifier
import gcf.sfa.trust.credential as cred
import gcf.sfa.trust.gid as gid

# See sfa/trust/rights.py
RENEWSLIVERPRIV = 'renewsliver'
RESOURCEPUBLICIDPREFIX = 'geni.net'
CREATESLIVERPRIV = 'createsliver'
DELETESLIVERPRIV = 'deleteslice'
SLIVERSTATUSPRIV = 'getsliceresources'

MAXLEASE_DAYS = 365

class AggregateManager(object):
    
    def __init__(self, root_cert, proxy_url):
        self._cred_verifier = CredentialVerifier(root_cert)
        self.max_lease = datetime.timedelta(days=MAXLEASE_DAYS)
        self.logger = logging.getLogger("gam")
        if proxy_url.startswith("https"):
            self.proxy = xmlrpclib.ServerProxy(proxy_url,
                                               xmlrpclib.SafeTransport())
        else:
            self.proxy = xmlrpclib.ServerProxy(proxy_url)

    def GetVersion(self):
        self.logger.info("Called GetVersion")
        return self.proxy.GetVersion()

    def ListResources(self, credentials, options):
        self.logger.info('ListResources(%r)' % (options))
        #privileges = ('listresources',)
        privileges = ()
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                credentials,
                                                None,
                                                privileges)
        retval = self.proxy.ListResources(credentials, options)
        return retval
    
    def CreateSliver(self, slice_urn, credentials, rspec, users):
        self.logger.info('CreateSliver(%r)' % (slice_urn))
        privileges = (CREATESLIVERPRIV,)
        creds = self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                        credentials,
                                                        slice_urn,
                                                        privileges)
        # FIXME: users arg!!
        return self.proxy.CreateSliver(slice_urn, credentials, rspec)

    def DeleteSliver(self, slice_urn, credentials):
        self.logger.info('DeleteSliver(%r)' % (slice_urn))
        privileges = (DELETESLIVERPRIV,)
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                credentials,
                                                slice_urn,
                                                privileges)
        return self.proxy.DeleteSliver(slice_urn, credentials)
    
    def SliverStatus(self, slice_urn, credentials):
        self.logger.info('SliverStatus(%r)' % (slice_urn))
        privileges = (SLIVERSTATUSPRIV,)
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                credentials,
                                                slice_urn,
                                                privileges)
        return self.proxy.SliverStatus()
    
    def RenewSliver(self, slice_urn, credentials, expiration_time):
        self.logger.info('RenewSliver(%r, %r)' % (slice_urn, expiration_time))
        privileges = (RENEWSLIVERPRIV,)
        creds = self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                        credentials,
                                                        slice_urn,
                                                        privileges)
        return self.proxy.RenewSliver(slice_urn, credentials, expiration_time)
    
    def Shutdown(self, slice_urn, credentials):
        self.logger.info('Shutdown(%r)' % (slice_urn))
        # TODO: No permission for Shutdown currently exists.
        privileges = ()
        self._cred_verifier.verify_from_strings(self._server.pem_cert,
                                                        credentials,
                                                        slice_urn,
                                                        privileges)
	return self.proxy.Shutdown(slice_urn, credentials)

def parse_args(argv):
    import socket
    parser = optparse.OptionParser()
    parser.add_option("-k", "--keyfile",
                      help="AM key file name", metavar="FILE")
    parser.add_option("-c", "--certfile",
                      help="AM certificate file name (PEM format)", metavar="FILE")
    parser.add_option("-r", "--rootcafile",
                      help="Root CA certificates file or directory name (PEM format)", metavar="FILE")
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
    if opts.debug:
        level = logging.DEBUG
    logging.basicConfig(level=level)
    
    if opts.rootcafile is None:
        sys.exit('Missing path to Root CAs file or directory (-r argument)')

    delegate = AggregateManager(opts.rootcafile, opts.url)

    # here rootcafile is supposed to be a single file with multiple
    # certs possibly concatenated together
    comboCertsFile = CredentialVerifier.getCAsFileFromDir(opts.rootcafile)

    ams = geni.AggregateManagerServer((opts.host, opts.port),
                                      delegate=delegate,
                                      keyfile=opts.keyfile,
                                      certfile=opts.certfile,
                                      ca_certs=comboCertsFile)
    logging.getLogger('gam').info('GENI AM Listening on port %d...' % (opts.port))
    ams.serve_forever()

if __name__ == "__main__":
    sys.exit(main())
