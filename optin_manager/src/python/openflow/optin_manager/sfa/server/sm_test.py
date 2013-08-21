import sys
import time
import traceback
from StringIO import StringIO
from copy import copy
from lxml import etree
#from sfa.sfaclientlib import SfaClientBootstrap
class SliceManager:

    # the cache instance is a class member so it survives across incoming requests
    cache = None

    def __init__ (self, config):
        self.cache=None

    def Resources(self):
        aggregate = {'hrn':'topdomain.nitos','addr':'192.168.254.188', 'port':8080}
        server = SfaServerProxy('192.168.254.188:8080') 
        server.ListResources(None,None)

import xmlrpclib
from httplib import HTTPS, HTTPSConnection
need_HTTPSConnection=hasattr(xmlrpclib.Transport().make_connection('localhost'),'getresponse')
class SfaServerProxy:

    def __init__ (self, url, keyfile=None, certfile=None, verbose=False, timeout=None):
        self.url=url
        self.keyfile=keyfile
        self.certfile=certfile
        self.verbose=verbose
        self.timeout=timeout
        # an instance of xmlrpclib.ServerProxy
        transport = XMLRPCTransport(keyfile, certfile, timeout)
        self.serverproxy = XMLRPCServerProxy(url, transport, allow_none=True, verbose=verbose)

    # this is python magic to return the code to run when 
    # SfaServerProxy receives a method call
    # so essentially we send the same method with identical arguments
    # to the server_proxy object
    def __getattr__(self, name):
        def func(*args, **kwds):
            return getattr(self.serverproxy, name)(*args, **kwds)
        return func

class XMLRPCServerProxy(xmlrpclib.ServerProxy):
    def __init__(self, url, transport, allow_none=True, verbose=False):
        # remember url for GetVersion
        # xxx not sure this is still needed as SfaServerProxy has this too
        self.url=url
        xmlrpclib.ServerProxy.__init__(self, url, transport, allow_none=allow_none, verbose=verbose)

    def __getattr__(self, attr):
        return xmlrpclib.ServerProxy.__getattr__(self, attr)

class XMLRPCTransport(xmlrpclib.Transport):

    def __init__(self, key_file=None, cert_file=None, timeout=None):
        xmlrpclib.Transport.__init__(self)
        self.timeout=timeout
        self.key_file = key_file
        self.cert_file = cert_file

    def make_connection(self, host):
        # create a HTTPS connection object from a host descriptor
        # host may be a string, or a (host, x509-dict) tuple
        host, extra_headers, x509 = self.get_host_info(host)
        if need_HTTPSConnection:
            conn = HTTPSConnection(host, None, key_file=self.key_file, cert_file=self.cert_file)
        else:
            conn = HTTPS(host, None, key_file=self.key_file, cert_file=self.cert_file)

        # Some logic to deal with timeouts. It appears that some (or all) versions
        # of python don't set the timeout after the socket is created. We'll do it
        # ourselves by forcing the connection to connect, finding the socket, and
        # calling settimeout() on it. (tested with python 2.6)
        if self.timeout:
            if hasattr(conn, 'set_timeout'):
                conn.set_timeout(self.timeout)

            if hasattr(conn, "_conn"):
                # HTTPS is a wrapper around HTTPSConnection
                real_conn = conn._conn
            else:
                real_conn = conn
            conn.connect()
            if hasattr(real_conn, "sock") and hasattr(real_conn.sock, "settimeout"):
                real_conn.sock.settimeout(float(self.timeout))
        return conn
       
    def getparser(self):
        unmarshaller = ExceptionUnmarshaller()
        parser = xmlrpclib.ExpatParser(unmarshaller)
        return parser, unmarshaller

class ExceptionUnmarshaller(xmlrpclib.Unmarshaller):
    def close(self):
        try:
            return xmlrpclib.Unmarshaller.close(self)
        except xmlrpclib.Fault, e:
            raise e.faultString


#client_bootstrap = SfaClientBootstrap('ocf.i2cat.user',None ,dir='/opt/ofelia/expedient/src/python/sfa/sfi/')
#cert = client_bootstrap.self_signed_cert_produce('/opt/ofelia/expedient/src/python/sfa/sfi/ocf.i2cat.user.sscert')
#print cert
#credential =  client_bootstrap.my_credential_produce ('/opt/ofelia/expedient/src/python/sfa/sfi/ocf.i2cat.user.cred')
#print credential
#cred = client_bootstrap.my_credential_string()
#print cred
credential = open('/opt/ofelia/optin_manager/src/python/openflow/optin_manager/sfa/credentials/ocf.cred','r')
#credential = open('/home/user/jfed_PEM/slicecred2.cred')
print credential

s = SfaServerProxy('https://192.168.254.188:12346','/opt/ofelia/expedient/src/python/sfa/topdomain.pkey', '/opt/ofelia/expedient/src/python/sfa/topdomain.gid')
s = SfaServerProxy('https://192.168.254.188:12346','/opt/ofelia/optin_manager/src/python/openflow/optin_manager/sfa/my_roots/authorities/ocf/ocf.pkey', '/opt/ofelia/optin_manager/src/python/openflow/optin_manager/sfa/my_roots/authorities/ocf/ocf.gid')

#print s.get_trusted_certs([credential.read()],{'cached': True, 'list_leases': 'resources', 'geni_rspec_version': {'type': 'SFA', 'version': '1', 'namespace': None, 'extensions': [], 'schema': None}, 'rspec_version': {'namespace': None, 'version': '1', 'type': 'SFA', 'extensions': [], 'schema': None}, 'call_id': 'urn:uuid:57a5ce8d-a668-497c-8e91-ba5c4b42d415'})

print s.get_trusted_certs('aaa')#credential.read())
