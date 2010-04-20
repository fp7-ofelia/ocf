#!/usr/bin/env python2.6

import optparse
import random
import sys
import urllib
import uuid
import xml.dom.minidom as minidom
import xmlrpclib

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
                                   verbose=True)
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
    if top.tagName != 'rspec':
        return None
    for node in top.childNodes:
        if node.tagName != 'resource':
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
    # XXX verify manifest_rspec
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

def exercise_am(host, port, keyfile, certfile, verbose=False):
    cert_transport = SafeTransportWithCert(keyfile=keyfile, certfile=certfile)
    url = 'https://%s' % (host)
    if port:
        url = '%s:%s' % (url, port)
    server = xmlrpclib.ServerProxy(url, transport=cert_transport,
                                   verbose=verbose)
    # Temporary until CH is connected
    slice_urn = str(uuid.uuid4())
    slice_credential = '<credential/>'
    credentials = list(slice_credential)

    print 'Testing GetVersion...',
    vdict = server.GetVersion()
    if vdict['geni_api'] == 1:
        print 'passed'
    else:
        print 'failed'

    print 'Testing ListResources...',
    options = dict()
    rspec = server.ListResources(credentials, options)
    dom = verify_rspec(rspec)
    if dom:
        print 'passed'
    else:
        print 'failed'

    test_create_sliver(server, slice_urn, credentials, dom)
    test_sliver_status(server, slice_urn, credentials)
    test_delete_sliver(server, slice_urn, credentials)

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
    parser.add_option("--ch", action="store_true", default=False,
                      help="exercise clearinghouse")
    return parser.parse_args()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts, args = parse_args(argv)
    if opts.ch:
        excercise_ch(opts.host, opts.port, opts.keyfile, opts.certfile)
    else:
        exercise_am(opts.host, opts.port, opts.keyfile, opts.certfile)
    return 0

if __name__ == "__main__":
    sys.exit(main())
