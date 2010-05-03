#!/usr/bin/env python2.6

import optparse
import random
import sys
import xml.dom.minidom as minidom
import xmlrpclib
import sfa.trust.credential as cred
from pprint import pprint
from client import SafeTransportWithCert

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
    rspec = '''
    <resv_rspec>
        <user
            fullname="John Doe"
            email="john.doe@geni.net"
            password="slice_pass"
        />
        <project
            name="Stanford Networking Group"
            description="Internet performance research to ..."
        />
        <slice
            name="Crazy Load Balancer"
            description="Does this and that..."
            controller_url="tcp:controller.stanford.edu:6633"
        />
        <flowspace>
            <switches>
                <switch dpid="0">
                <switch dpid="2">
            </switches>
            <policy value="1" />
            <port from="1" to="4" />
            <dl_src from="22:33:44:55:66:77" to="22:33:44:55:66:77" />
            <dl_dst from="*" to="*" />
            <dl_type from="0x800" to="0x800" />
            <vlan_id from="15" to="20" />
            <nw_src from="192.168.3.0" to="192.168.3.255" />
            <nw_dst from="192.168.3.0" to="192.168.3.255" />
            <nw_proto from="17" to="17" />
            <tp_src from="100" to="100" />
            <tp_dst from="100" to="*" />
        </flowspace>
        <flowspace>
            <switches>
                <switch dpid="1">
            </switches>
            <policy value="-1" />
            <tp_src from="100" to="100" />
            <tp_dst from="100" to="*" />
        </flowspace>
    </resv_rspec>
 '''    
    manifest_rspec = server.CreateSliver(slice_urn, slice_credential,
                                         rspec)
    if manifest_rspec != rspec:
        print 'failed'
    else:
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

def test_list_resources(server, credentials):
    print 'Testing ListResources...',
    options = dict()
    rspec = server.ListResources(credentials, options)
    print(rspec)
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
    #TODO: Fix expiration time
#    test_renew_sliver(am_server, slice_urn, credentials, 10)
#    test_delete_sliver(am_server, slice_urn, credentials)
    
#    # Now create a slice and shut it down instead of deleting it.
#    slice_cred_string = ch_server.CreateSlice()
#    slice_credential = cred.Credential(string=slice_cred_string)
#    slice_gid = slice_credential.get_gid_object()
#    slice_urn = slice_gid.get_urn()
#    print 'Second Slice URN = %s' % (slice_urn)
#    credentials = [slice_cred_string]
#    dom = test_list_resources(am_server, credentials)
#    test_create_sliver(am_server, slice_urn, credentials, dom)
#    test_shutdown(am_server, slice_urn, credentials)

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
    return parser.parse_args()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts = parse_args(argv)[0]
    ch_server = make_server(opts.ch, opts.keyfile, opts.certfile, opts.debug)
    am_server = make_server(opts.am, opts.keyfile, opts.certfile, opts.debug)
    exercise_am(ch_server, am_server)
    return 0

if __name__ == "__main__":
    sys.exit(main())
