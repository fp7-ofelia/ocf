### $Id$
### $URL$

import os
import sys
import datetime
import time
import xmlrpclib
from types import StringTypes, ListType

from sfa.util.geniserver import GeniServer
from sfa.util.storage import *
from sfa.util.faults import *
import sfa.util.xmlrpcprotocol as xmlrpcprotocol
import sfa.util.soapprotocol as soapprotocol

# GeniLight client support is optional
try:
    from egeni.geniLight_client import *
except ImportError:
    GeniClientLight = None


class Aggregate(GeniServer):

    ##
    # Create a new aggregate object.
    #
    # @param ip the ip address to listen on
    # @param port the port to listen on
    # @param key_file private key filename of registry
    # @param cert_file certificate filename containing public key (could be a GID file)     
    def __init__(self, ip, port, key_file, cert_file):
        GeniServer.__init__(self, ip, port, key_file, cert_file)
        self.server.interface = 'aggregate'

##
# Aggregates is a dictionary of geniclient aggregate connections keyed on the aggregate hrn

class Aggregates(dict):

    required_fields = ['hrn', 'addr', 'port']
     
    def __init__(self, api, file = "/etc/sfa/aggregates.xml"):
        dict.__init__(self, {})
        self.api = api
        self.interfaces = []
        # create default connection dict
        connection_dict = {}
        for field in self.required_fields:
            connection_dict[field] = ''
        aggregates_dict = {'aggregates': {'aggregate': [connection_dict]}}
        # get possible config file locations
        loaded = False
        path = os.path.dirname(os.path.abspath(__file__))
        filename = file.split(os.sep)[-1]
        alt_file = path + os.sep + filename
        files = [file, alt_file]
        
        for f in files:
            try:
                if os.path.isfile(f):
                    self.aggregate_info = XmlStorage(f, aggregates_dict)
                    loaded = True
            except: pass

        # if file is missing, just recreate it in the right place
        if not loaded:
            self.aggregate_info = XmlStorage(file, aggregates_dict)
        self.aggregate_info.load()
        self.connectAggregates()

    def connectAggregates(self):
        """
        Get connection details for the trusted peer aggregates from file and 
        create an GeniClient connection to each. 
        """
        aggregates = self.aggregate_info['aggregates']['aggregate']
        if isinstance(aggregates, dict):
            aggregates = [aggregates]
        if isinstance(aggregates, list):
            for aggregate in aggregates:
                # make sure the required fields are present
                if not set(self.required_fields).issubset(aggregate.keys()):
                    continue
                hrn, address, port = aggregate['hrn'], aggregate['addr'], aggregate['port']
                if not hrn or not address or not port:
                    continue
                self.interfaces.append(aggregate)
                # check which client we should use
                # geniclient is default
                client_type = 'geniclient'
                if aggregate.has_key('client') and aggregate['client'] in ['geniclientlight']:
                    client_type = 'geniclientlight'
                
                # create url
                url = 'http://%(address)s:%(port)s' % locals()

                # create the client connection
                # make sure module exists before trying to instantiate it
                if client_type in ['geniclientlight'] and GeniClientLight:
                    self[hrn] = GeniClientLight(url, self.api.key_file, self.api.cert_file)
                else:
                    self[hrn] = xmlrpcprotocol.get_server(url, self.api.key_file, self.api.cert_file)

        # set up a connection to the local registry
        # connect to registry using GeniClient
        address = self.api.config.SFA_AGGREGATE_HOST
        port = self.api.config.SFA_AGGREGATE_PORT
        url = 'http://%(address)s:%(port)s' % locals()
        local_aggregate = {'hrn': self.api.hrn, 'addr': address, 'port': port}
        self.interfaces.append(local_aggregate) 
        self[self.api.hrn] = xmlrpcprotocol.get_server(url, self.api.key_file, self.api.cert_file)


