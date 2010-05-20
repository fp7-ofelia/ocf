#!/usr/bin/env python2.6

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

import base64
import datetime
import logging
import optparse
import random
import sys
import xml.dom.minidom as minidom
import xmlrpclib
import zlib
import gcf.sfa.trust.credential as cred

class SafeTransportWithCert(xmlrpclib.SafeTransport):

    def __init__(self, use_datetime=0, keyfile=None, certfile=None):
        xmlrpclib.SafeTransport.__init__(self, use_datetime)
        self.__x509 = dict()
        if keyfile:
            self.__x509['key_file'] = keyfile
        if certfile:
            self.__x509['cert_file'] = certfile

    def make_connection(self, host):
        host_tuple = (host, self.__x509)
        return xmlrpclib.SafeTransport.make_connection(self, host_tuple)


def exercise_ch(host, port, keyfile, certfile):
    cert_transport = SafeTransportWithCert(keyfile=keyfile, certfile=certfile)
    url = 'https://%s' % (host)
    if port:
        url = '%s:%s' % (url, port)
    server = xmlrpclib.ServerProxy(url, transport=cert_transport,
                                   verbose=False)
    print server
    try:
        print server.GetVersion()
    except xmlrpclib.Error, v:
        print 'ERROR', v
    try:
        print server.CreateSlice()
    except xmlrpclib.Error, v:
        print 'ERROR', v

def verify_rspec(rspec):
    # It should be parseable XML
    # The top level node should be named 'rspec'
    # The children of the top level node should all be named 'resource'
    dom = minidom.parseString(rspec)
    top = dom.documentElement
    if top.tagName.lower() != 'rspec':
        return None
    return dom

def test_create_sliver(server, slice_urn, slice_credential, dom):
    print 'Testing CreateSliver...',
    resources = dom.getElementsByTagName('resource')
    dom_impl = minidom.getDOMImplementation()
    request_rspec = dom_impl.createDocument(None, 'rspec', None)
    top = request_rspec.documentElement
    if resources.length == 0:
        print 'failed: no resources available'
    elif resources.length == 1:
        top.appendChild(resources.item(0).cloneNode(True))
    else:
        # pick two at random
        indices = range(resources.length)
        for i in range(2):
            index = random.choice(indices)
            indices.remove(index)
            top.appendChild(resources.item(index).cloneNode(True))
    manifest_rspec = server.CreateSliver(slice_urn, slice_credential,
                                         request_rspec.toxml())
    # TODO: verify manifest_rspec
    print 'passed'

def test_delete_sliver(server, slice_urn, slice_credential):
    print 'Testing DeleteSliver...',
    try:
        result = server.DeleteSliver(slice_urn, slice_credential)
        if result is True:
            print 'passed'
        else:
            print 'failed'
    except xmlrpclib.Error, v:
        print 'ERROR', v

def test_sliver_status(server, slice_urn, credentials):
    print 'Testing SliverStatus...',
    result = server.SliverStatus(slice_urn, credentials)
#    import pprint
#    pprint.pprint(result)
    sliver_keys = frozenset(('geni_urn', 'geni_status', 'geni_resources'))
    resource_keys = frozenset(('geni_urn', 'geni_status', 'geni_error'))
    errors = list()
    missing = sliver_keys - set(result.keys())
    if missing:
        errors.append('missing keys %r' % (missing))
    if 'geni_resources' in result:
        for resource in result['geni_resources']:
            missing = resource_keys - set(resource.keys())
            if missing:
                errors.append('missing resource keys %r' % (missing))
    if errors:
        print 'failed'
        for x in errors:
            print '\t', x
    else:
        print 'passed'
        
def test_renew_sliver(server, slice_urn, credentials, expiration_time):
    print 'Testing RenewSliver...',
    result = server.RenewSliver(slice_urn, credentials, expiration_time)
    if result is True or result is False:
        print 'passed'
    else:
        print 'failed'
        print 'returned %r instead of boolean value' % (result)

def test_shutdown(server, slice_urn, credentials):
    print 'Testing Shutdown...',
    result = server.Shutdown(slice_urn, credentials)
    if result is True or result is False:
        print 'passed'
    else:
        print 'failed'
        print 'returned %r instead of boolean value' % (result)

def test_get_version(server):
    print 'Testing GetVersion...',
    vdict = server.GetVersion()
    if vdict['geni_api'] == 1:
        print 'passed'
    else:
        print 'failed'

def test_list_resources(server, credentials, compressed=False, available=True,
                        slice_urn=None):
    print 'Testing ListResources...',
    options = dict(geni_compressed=compressed, geni_available=available)
    if slice_urn:
        options['geni_slice_urn'] = slice_urn
    rspec = server.ListResources(credentials, options)
    if compressed:
        rspec = zlib.decompress(base64.b64decode(rspec))
    logging.debug(rspec)
    dom = verify_rspec(rspec)
    if dom:
        print 'passed'
    else:
        print 'failed'
    return dom

def exercise_am(ch_server, am_server):
    # Create a slice at the clearinghouse
    slice_cred_string = ch_server.CreateSlice()
    slice_credential = cred.Credential(string=slice_cred_string)
    slice_gid = slice_credential.get_gid_object()
    slice_urn = slice_gid.get_urn()
    print 'Slice URN = %s' % (slice_urn)
    
    # Set up the array of credentials as just the slice credential
    credentials = [slice_cred_string]

    test_get_version(am_server)
    dom = test_list_resources(am_server, credentials)
    test_create_sliver(am_server, slice_urn, credentials, dom)
    test_sliver_status(am_server, slice_urn, credentials)
    test_list_resources(am_server, credentials, slice_urn=slice_urn)
    
    expiration = datetime.datetime.now() + datetime.timedelta(days=1)
    test_renew_sliver(am_server, slice_urn, credentials, expiration)
    
    test_delete_sliver(am_server, slice_urn, credentials)
    
    # Test compression on list resources
    dom = test_list_resources(am_server, credentials, compressed=True,
                              available=False)

    # Now create a slice and shut it down instead of deleting it.
    slice_cred_string = ch_server.CreateSlice()
    slice_credential = cred.Credential(string=slice_cred_string)
    slice_gid = slice_credential.get_gid_object()
    slice_urn = slice_gid.get_urn()
    print 'Second Slice URN = %s' % (slice_urn)
    credentials = [slice_cred_string]
    dom = test_list_resources(am_server, credentials)
    test_create_sliver(am_server, slice_urn, credentials, dom)
    test_shutdown(am_server, slice_urn, credentials)

def make_server(url, keyfile, certfile, verbose=False):
    """Create an SSL connection to an XML RPC server.
    Returns the XML RPC server proxy.
    """
    cert_transport = SafeTransportWithCert(keyfile=keyfile, certfile=certfile)
    return xmlrpclib.ServerProxy(url, transport=cert_transport,
                                 verbose=verbose)
    
def parse_args(argv):
    parser = optparse.OptionParser()
    parser.add_option("-k", "--keyfile",
                      help="key file name", metavar="FILE")
    parser.add_option("-c", "--certfile",
                      help="certificate file name", metavar="FILE")
    # Could try to determine the real IP Address instead of the loopback
    # using socket.gethostbyname(socket.gethostname())
    parser.add_option("-H", "--host", default='127.0.0.1',
                      help="server ip", metavar="HOST")
    parser.add_option("-p", "--port", type=int, default=8000,
                      help="server port", metavar="PORT")
    parser.add_option("--ch", default='https://localhost:8000/',
                      help="clearinghouse URL")
    parser.add_option("--am", default='https://localhost:8001/',
                      help="aggregate manager URL")
    parser.add_option("--debug", action="store_true", default=False,
                       help="enable debugging output")
    parser.add_option("--debug-rpc", action="store_true", default=False,
                      help="enable XML RPC debugging")
    return parser.parse_args()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts = parse_args(argv)[0]
    level = logging.INFO
    if opts.debug:
        level = logging.DEBUG
    logging.basicConfig(level=level)
    ch_server = make_server(opts.ch, opts.keyfile, opts.certfile,
                            opts.debug_rpc)
    am_server = make_server(opts.am, opts.keyfile, opts.certfile,
                            opts.debug_rpc)
    exercise_am(ch_server, am_server)
    return 0

if __name__ == "__main__":
    sys.exit(main())
