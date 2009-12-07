#
# Registry is a GeniServer that implements the Registry interface
#
### $Id: registry.py 14821 2009-08-19 01:20:13Z tmack $
### $URL: http://svn.planet-lab.org/svn/sfa/tags/sfa-0.9-5/sfa/server/registry.py $
#

import tempfile
import os
import time
import sys

from sfa.util.geniserver import GeniServer
from sfa.util.geniclient import GeniClient
from sfa.util.genitable import GeniTable
from sfa.util.faults import *
from sfa.util.storage import *

# GeniLight client support is optional
try:
    from egeni.geniLight_client import *
except ImportError:
    GeniClientLight = None            

##
# Registry is a GeniServer that serves registry and slice operations at PLC.

class Registry(GeniServer):
    ##
    # Create a new registry object.
    #
    # @param ip the ip address to listen on
    # @param port the port to listen on
    # @param key_file private key filename of registry
    # @param cert_file certificate filename containing public key (could be a GID file)

    def __init__(self, ip, port, key_file, cert_file):
        GeniServer.__init__(self, ip, port, key_file, cert_file)
        self.server.interface = 'registry' 


##
# Registries is a dictionary of geniclient registry connections keyed on the registry
# hrn

class Registries(dict):

    required_fields = ['hrn', 'addr', 'port']

    def __init__(self, api, file = "/etc/sfa/registries.xml"):
        dict.__init__(self, {})
        self.api = api
        self.interfaces = []
       
        # create default connection dict
        connection_dict = {}
        for field in self.required_fields:
            connection_dict[field] = ''
        registries_dict = {'registries': {'registry': [connection_dict]}}

        # get possible config file locations
        loaded = False
        path = os.path.dirname(os.path.abspath(__file__))
        filename = file.split(os.sep)[-1]
        alt_file = path + os.sep + filename
        files = [file, alt_file]
    
        for f in files:
            try:
                if os.path.isfile(f):
                    self.registry_info = XmlStorage(f, registries_dict)
                    loaded = True
            except: pass

        # if file is missing, just recreate it in the right place
        if not loaded:
            self.registry_info = XmlStorage(file, registries_dict)
        self.registry_info.load()
        self.connectRegistries()
        
    def connectRegistries(self):
        """
        Get connection details for the trusted peer registries from file and 
        create an GeniClient connection to each. 
        """
        registries = self.registry_info['registries']['registry']
        if isinstance(registries, dict):
            registries = [registries]
        if isinstance(registries, list):
            for registry in registries:
                # make sure the required fields are present
                if not set(self.required_fields).issubset(registry.keys()):
                    continue
                hrn, address, port = registry['hrn'], registry['addr'], registry['port']
                if not hrn or not address or not port:
                    continue
                self.interfaces.append(registry)
                # check which client we should use
                # geniclient is default
                client_type = 'geniclient'
                if registry.has_key('client') and registry['client'] in ['geniclientlight']:
                    client_type = 'geniclientlight'
                
                # create url
                url = 'http://%(address)s:%(port)s' % locals()

                # create the client connection
                # make sure module exists before trying to instantiate it
                if client_type in ['geniclientlight'] and GeniClientLight:
                    self[hrn] = GeniClientLight(url, self.api.key_file, self.api.cert_file) 
                else:    
                    self[hrn] = GeniClient(url, self.api.key_file, self.api.cert_file)

        # set up a connection to the local registry
        # connect to registry using GeniClient
        address = self.api.config.SFA_REGISTRY_HOST
        port = self.api.config.SFA_REGISTRY_PORT
        url = 'http://%(address)s:%(port)s' % locals()
        local_registry = {'hrn': self.api.hrn, 'addr': address, 'port': port}
        self.interfaces.append(local_registry)
        self[self.api.hrn] = GeniClient(url, self.api.key_file, self.api.cert_file)            
    
