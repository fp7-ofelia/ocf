#----------------------------------------------------------------------
# Copyright (c) 2012-2013 Raytheon BBN Technologies
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
'''An aggregate that is actually a thin proxy to the real aggregate.
Uses the GENI Clearinghouse services.
Speaks only AM API v2.'''

import logging
import os

import geni
from geni.am.am2 import AggregateManager
from geni.am.am2 import AggregateManagerServer
from geni.am.am2 import ReferenceAggregateManager
from geni.SecureXMLRPCServer import SecureXMLRPCServer
from geni.util.ch_interface import *
from omnilib.xmlrpc.client import make_client

SR_URL = "https://" + socket.gethostname() + "/sr/sr_controller.php"

class ProxyAggregateManager(ReferenceAggregateManager):

    "A manager that responds to AM API and passes on requests to another AM"

    # URL of MA controller in CH
    ma_url = None

    # URL of actual AM to which we're connecting
    am_url = None

    # *** TO DO ***
    # keep a cache of member_id => key/cert
    # And a cache of connections

    def __init__(self, am_url, root_cert, urn_authority):
        super(ProxyAggregateManager, self).__init__(root_cert, urn_authority);
        self.am_url = am_url
#        print("SELF.AM_URL = " + self.am_url)
        dictargs = dict(service_type=3) # Member Authority
        ma_services = invokeCH(SR_URL, 'get_services_of_type', self.logger, dictargs);
        if(ma_services['code'] == 0):
            ma_service_row = ma_services['value'][0]
            self.ma_url = ma_service_row['service_url']
            # print("MA_URL " + str(self.ma_url)) 
        self.logger = logging.getLogger('gcf.pxam')

    # Helper function to create a proxy client that talks 
    # to real AM using inside keys
    def make_proxy_client(self):
        key_certs = get_inside_cert_and_key(self._server.peercert, \
                                                self.ma_url, self.logger);
        key_fname = key_certs['key'];
        cert_fname = key_certs['cert'];
        client = make_client(self.am_url, key_fname, cert_fname)
        client.key_fname = key_fname;
        client.cert_fname = cert_fname;
        return client;

    def close_proxy_client(self, client):
        os.unlink(client.key_fname);
        os.unlink(client.cert_fname);

    # *** GetVersion should return something to indicate there is a proxy
    def GetVersion(self, options):
        client = self.make_proxy_client();
        client_ret = None;
        try:
            client_ret = client.GetVersion();
        except Exception:
            print "Error in remote GetVersion call";
        print("GetVersion.CLIENT_RET = " + str(client_ret));
        self.close_proxy_client(client);
        return client_ret;

    def ListResources(self, credentials, options):
        client = self.make_proxy_client();
#        # Shouldn't need this - it is an indication of an version mismatch
#        options['geni_rspec_version'] = dict(type='geni', version='3');
#        print("OPTS = " + str(options));
#        print("CREDS = " + str(credentials));
        try:
            client_ret = client.ListResources(credentials, options);
        except Exception:
            print "Error in remote ListResources call";
        print("ListResources.CLIENT_RET = " + str(client_ret));
        # Why do I need to do this?
#        client_ret = client_ret['value'];
        self.close_proxy_client(client);
        return client_ret;

    def CreateSliver(self, slice_urn, credentials, rspec, users, options):
#        print("URN = " + str(slice_urn));
#        print("OPTS = " + str(options));
#        print("CREDS = " + str(credentials));
#        print("RSPEC = " + str(rspec));
#        print("USERS = " + str(users));
        client = self.make_proxy_client();
        try:
            client_ret = client.CreateSliver(slice_urn, credentials, rspec, users, options);
        except Exception:
            print "Error in remote CreateSliver call";
#        print("CreateSliver.CLIENT_RET = " + str(client_ret));
        self.close_proxy_client(client);
        return client_ret;
            
    def DeleteSliver(self, slice_urn, credentials, options):
        client = self.make_proxy_client();
        try:
            client_ret = client.DeleteSliver(slice_urn, credentials, options);
        except Exception:
            print "Error in remote DeleteSliver call";
        self.close_proxy_client(client);
        return client_ret;

    def SliverStatus(self, slice_urn, credentials, options):
        client = self.make_proxy_client();
        try:
            client_ret = client.SliverStatus(slice_urn, credentials, options);
        except Exception:
            print "Error in remote SliverStatus call";
        self.close_proxy_client(client);
        return client_ret;

    def RenewSliver(self, slice_urn, credentials, expiration_time, options):
        client = self.make_proxy_client();
        try:
            client_ret = client.RenewSliver(slice_urn, credentials, expiration_time, options);
        except Exception:
            print "Error in remote RenewSliver call"
        self.close_proxy_client(client);
        return client_ret;

    def Shutdown(self, slice_urn, credentials, options):
        client = self.make_proxy_client();
        try:
            client_ret = client.Shutdown(slice_urn, credentials, options);
        except Exception:
            print "Error in remote Shutdown call"
        self.close_proxy_client(client);
        return client_ret;

class ProxyAggregateManagerServer(AggregateManagerServer):
    "A server that provides the AM API to tools, but passes requests"
    "to a real configured AM, after logging and authorizing"

    def __init__(self, addr, am_url, keyfile=None, certfile=None,
                 trust_roots_dir=None,
                 ca_certs=None, base_name=None):
        # ca_certs arg here must be a file of concatenated certs
        if ca_certs is None:
            raise Exception('Missing CA Certs')
        elif not os.path.isfile(os.path.expanduser(ca_certs)):
            raise Exception('CA Certs must be an existing file of accepted root certs: %s' % ca_certs)

        delegate = ProxyAggregateManager(am_url, trust_roots_dir, base_name)
        self._server = SecureXMLRPCServer(addr, keyfile=keyfile,
                                          certfile=certfile, ca_certs=ca_certs)
        self._server.register_instance(AggregateManager(delegate))
        # Set the server on the delegate so it can access the
        # client certificate.
        delegate._server = self._server

        if not base_name is None:
            global RESOURCE_NAMESPACE
            RESOURCE_NAMESPACE = base_name

   
