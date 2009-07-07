##
# This module implements the client-side of the Geni API. Stubs are provided
# that convert the supplied parameters to the necessary format and send them
# via XMLRPC to a Geni Server.
#
# TODO: Investigate ways to combine this with existing PLC API?
##

from __future__ import with_statement

import xmlrpclib

from geni.util.gid import *
from geni.util.credential import *
from geni.util.record import *
from geni.util.geniticket import *
from suds.client import Client
from suds.xsd.sxbasic import Import

wsdl_file_location = 'http://yuba.stanford.edu/geniLight/geniLight.wsdl'

##
# The GeniLightClient class provides stubs for executing Geni operations. A given
# client object connects to one server. To connect to multiple servers, create
# multiple GeniLightClient objects.
#
# The Geni protocol uses an HTTPS connection, and the client's side of the
# connection uses his private key. Generally, this private key must match the
# public key that is containing in the GID that the client is providing for
# those functions that take a GID.

class GeniLightClient():
    ##
    # Create a new GeniLightClient object.
    #
    # @param url is the url of the server
    # @param key_file = private key file of client
    # @param cert_file = x.509 cert containing the client's public key. This
    #      could be a GID certificate, or any x.509 cert.

    def __init__(self, url, key_file, cert_file):
        ns = 'http://schemas.xmlsoap.org/soap/encoding/'
        location = 'http://schemas.xmlsoap.org/soap/encoding/'
        Import.bind(ns, location)
        schema1 = 'http://schemas.xmlsoap.org/wsdl/soap/'
        schema2 = 'http://schemas.xmlsoap.org/wsdl/'
        schema3 = 'http://www.w3.org/2001/XMLSchema'
        Import.bind(schema1,schema1)
        Import.bind(schema2,schema2)
        Import.bind(schema3,schema3)
        self.server= Client(wsdl_file_location, location=url)

    # -------------------------------------------------------------------------
    # Registry Interface
    # -------------------------------------------------------------------------

    def create_gid(self, cred, name, uuid, pkey_string):
        return -1

    def get_gid(self, name):
        return []

    def get_self_credential(self, type, name):
        return None

    def get_credential(self, cred, type, name):
        return None

    def list(self, cred, hrn):
        return []

    def register(self, cred, record):
        return -1

    ##
    # Remove an object from the registry. If the object represents a PLC object,
    # then the PLC records will also be removed.
    #
    # @param cred credential object specifying rights of the caller
    # @param type
    # @param hrn

    def remove(self, cred, type, hrn):
        result = self.server.service.remove(hrn)
        return result

    def resolve(self, cred, name):
        return []

    def update(self, cred, record):
        return None


    #-------------------------------------------------------------------------
    # Aggregate Interface
    #-------------------------------------------------------------------------
    
    def test_func_call(self):
        return "Function call test succeeded."
    
    ## list components
    #
    # 
    def list_nodes(self, cred):
        result = self.server.service.list_components()
        return result

    def get_resources(self, cred, hrn):
        return None

    def get_policy(self, cred):
        return None

    ## create slice
    #
    # @param cred a credential
    # @param rspec resource specification defining how to instantiate the slice
    
    def create_slice(self, cred, hrn, rspec):
        u = UserSliceInfo(cred.save_to_string(save_parents=True), hrn)
        result = self.server.service.create_slice(u, str(rspec))
        return result


    ## delete slice
    #
    # @param cred a credential
    # @param hrn slice to delete
    def delete_slice(self, cred, hrn):
        u = UserSliceInfo(cred.save_to_string(save_parents=True), hrn)
        result = self.server.service.delete_slice(u)
        return result    

    # ------------------------------------------------------------------------
    # Slice Interface
    # ------------------------------------------------------------------------

    ##
    # Start a slice.
    #
    # @param cred a credential identifying the caller (callerGID) and the slice
    #     (objectGID)

    def start_slice(self, cred, hrn=None):
        result = self.server.service.start_slice( (cred.save_to_string(save_parents=True), hrn ))
        return result

    ##
    # Stop a slice.
    #
    # @param cred a credential identifying the caller (callerGID) and the slice
    #     (objectGID)

    def stop_slice(self, cred, hrn=None):
        u = UserSliceInfo(cred.save_to_string(save_parents=True), hrn)
        result = self.server.service.stop_slice(u)
        return result

    ##
    # List the slices on a component.
    #
    # @param cred credential object that authorizes the caller
    #
    # @return a list of slice names

    def list_slices(self, cred):
        result = self.server.service.list_slices()
        return result

    def get_ticket(self, cred, name, rspec):
        return None

    def redeem_ticket(self, ticket):
        return None

    def reset_slice(self, cred):
        return None


if __name__ == '__main__' :

    AGGREGATE_MANAGER_SOAP_IP = 'localhost'
    AGGREGATE_MANAGER_SOAP_IP = 7889

    glc = GeniLightClient('http://'+AGGREGATE_MANAGER_SOAP_IP + ':' + str(AGGREGATE_MANAGER_SOAP_PORT),'/dev/null','/dev/null')

    cred = Credential(subject='Alice')
    result = glc.list_nodes(cred)
    print result

    #result = glc.create_slice(cred, 'alice@testing.org')
    #print result
    
