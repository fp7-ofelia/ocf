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

import logging
import os
import socket
import ssl
import sys
import time
from urlparse import urlparse
import xmlrpclib

from omnilib.xmlrpc.client import make_client
from omnilib.frameworks.framework_base import Framework_Base

# The key is a converted pkcs12 file. Start with your ProtoGENI
# encrypted.p12 file (found in the .ssl directory or downloaded
# from the emulab site web page). Then convert it to pem using
# openssl:
#
#   $ openssl pkcs12 -in encrypted.p12 -out pgcert.pem -nodes
#
# That command will create a pgcert.pem file, which contains
# the private key you need. This resulting key is not password
# protected. See the openssl pkcs12 man page for more info.


class Framework(Framework_Base):
    """The ProtoGENI backend for Omni. This class defines the
    interface to the Protogeni Control Framework.
    """

    def __init__(self, config):
        self.logger = logging.getLogger("omni.protogeni")
        config['cert'] = os.path.expanduser(config['cert'])
        if not os.path.exists(config['cert']):
            sys.exit('PG Framework certfile %s doesnt exist' % config['cert'])
        config['key'] = os.path.expanduser(config['key'])
        if not os.path.exists(config['key']):
            sys.exit('PG Framework keyfile %s doesnt exist' % config['key'])
        if not config.has_key('verbose'):
            config['verbose'] = False
	else:
	    config['verbose'] = config['verbose'].lower() in ['true', '1', 't', 'yes', 'on']
	if config['verbose']:
		self.logger.info('Verbose logging is on')
        self.config = config
        self.logger.debug("Configured with key file %s", config['key'])
        
        self.logger.debug('Using clearinghouse %s', self.config['ch'])
        self.ch = make_client(self.config['ch'], self.config['key'],
                              self.config['cert'], self.config['verbose'])
        self.logger.debug('Using slice authority %s', self.config['sa'])
        self.sa = make_client(self.config['sa'], self.config['key'],
                              self.config['cert'], self.config['verbose'])
        self.user_cred = None
        
        # For now, no override aggregates.
        self.aggs = None
        # Hardcode the PG in ELab instance because it does not
        # show up in the clearinghouse.
        #self.aggs = {
            # Tom's inner emulab
            #'urn:publicid:IDN+elabinelab.geni.emulab.net':
            #    'https://myboss.elabinelab.geni.emulab.net:443/protogeni/xmlrpc/am'
            # Leigh's inner emulab
            # 'urn:publicid:IDN+myelab.testbed.emulab.net':
                # 'https://myboss.myelab.testbed.emulab.net:443/protogeni/xmlrpc/am'
            # Utah ProtoGENI
            #'urn:publicid:IDN+emulab.net':
                #'https://boss.emulab.net:443/protogeni/xmlrpc/am'
        #}
        
    def get_user_cred(self):
        if self.user_cred == None:
            pg_response = dict()
            try:
                pg_response = self.sa.GetCredential()
            except Exception as exc:
                self.logger.error('Using PG failed to call SA GetCredential using SA %s, cert %s: %s' % (self.config['sa'], self.config['cert'], exc))
                raise Exception('Using PG failed to call SA GetCredential using SA %s, cert %s: %s' % (self.config['sa'], self.config['cert'], exc))
                                  
            code = pg_response['code']
            if code:
                self.logger.error("Received error code: %d", code)
                output = pg_response['output']
                self.logger.error("Received error message: %s", output)
                #return None
            else:
                self.user_cred = pg_response['value']
        return self.user_cred
    
    def get_slice_cred(self, urn):
        mycred = self.get_user_cred()
        # Note params may be used again later in this method
        params = {'credential': mycred,
                  'type': 'Slice',
                  'urn': urn}
        self.logger.debug("Resolving %s at slice authority", urn)
        response = self.sa.Resolve(params)
        # response is a dict with three keys: code, value and output
        self.logger.debug("Got resolve response %r", response)
        if response['code']:
            # Unable to resolve, slice does not exist
            raise Exception('Slice %s does not exist.' % (urn))
        else:
            # Slice exists, get credential and return it
            self.logger.debug("Resolved slice %s, getting credential", urn)
            response = self.sa.GetCredential(params)
            return response['value']

    
    def slice_name_to_urn(self, name):
        """Convert a slice name to a slice urn."""
        #
        # Sample URNs:
        #   urn:publicid:IDN+pgeni3.gpolab.bbn.com+slice+tom1
        #   urn:publicid:IDN+elabinelab.geni.emulab.net+slice+tom1
        #

        # FIXME: Use credential.publicid_to_urn or similar
        # and take out this base constant - ugly

        base = 'urn:publicid:IDN+'
        url = urlparse(self.config['sa'])
        sa_host = url.hostname
        auth = sa_host[sa_host.index('.')+1:]
        if name.startswith(base):
            if not name.startswith(base+auth+"+slice+"):
                raise Exception("Incorrect slice name")
            return name
        
        if name.startswith(auth):            
            return base + name

        if '+' in name:
            raise Exception("Incorrect slice name")
        
        return base + auth + "+slice+" + name
        
        #slice_name = '%s+slice+%s' % (pg_site, name)
        #return namespace.long_urn(slice_name)
    
    def create_slice(self, urn):
        """Create a slice at the PG Slice Authority.
        If the slice exists, just return a credential for the existing slice.
        If the slice does not exist, create it and return a credential.
        """
        mycred = self.get_user_cred()
        # Note: params is used again below through either code path.
        params = {'credential': mycred,
                  'type': 'Slice',
                  'urn': urn}
        self.logger.debug("Resolving %s at slice authority", urn)
        response = self.sa.Resolve(params)
        # response is a dict with three keys: code, value and output
        self.logger.debug("Got resolve response %r", response)
        if response['code']:
            # Unable to resolve, create a new slice
            self.logger.debug("Creating new slice %s", urn)
            response = self.sa.Register(params)
            self.logger.debug("Got register response %r", response)
            return response['value']
        else:
            # Slice exists, get credential and return it
            self.logger.debug("Resolved slice %s, getting credential", urn)
            response = self.sa.GetCredential(params)
            return response['value']

    def delete_slice(self, urn):
        # It appears that delete_slice should return something. I'll return a string.
        return 'ProtoGENI does not support deleting slices. Slices are automatically removed when they expire.'

    def list_aggregates(self):
        if self.aggs:
            return self.aggs
        cm_dicts = self._get_components()
        am_dicts = self._find_geni_ams(cm_dicts)
        result = dict()
        for am_dict in am_dicts:
            self.logger.debug("Keys: %r", am_dict.keys())
            result[am_dict['urn']] = am_dict['am_url']
        for key, value in result.items():
            self.logger.debug('Found aggregate %r: %r', key, value)
        return result

    def renew_slice(self, urn, expiration_dt):
        """See framework_base for doc.
        """
        mycred = self.get_user_cred()
        # Note: params is used again below through either code path.
        params = {'credential': mycred,
                  'type': 'Slice',
                  'urn': urn}
        response = self.sa.GetCredential(params)
        if response['code']:
            msg = "Unable to get slice credential for slice %s: %s"
            msg = msg % (urn, response['output'])
            self.logger.warning(msg)
            return None
        else:
            slice_cred = response['value']
            expiration = expiration_dt.isoformat()
            self.logger.info('requesting new expiration %r', expiration)
            params = {'credential': slice_cred,
                      'expiration': expiration}
            response = self.sa.RenewSlice(params)
            if response['code']:
                # request failed, print a message and return None
                msg = "Failed to renew slice %s: %s"
                msg = msg % (urn, response['output'])
                self.logger.warning(msg)
                return None
            else:
                # Success. requested expiration worked, return it.
                return expiration_dt

    def _get_components(self):
        """Gets the ProtoGENI component managers from the ProtoGENI
        Clearinghouse. Returns a list of dictionaries as documented
        in https://www.protogeni.net/trac/protogeni/wiki/ClearingHouseAPI2#ListComponents
        """
        cred = self.get_user_cred()
        if not cred:
            raise Exception("No user credential available.")
        pg_response = self.ch.ListComponents({'credential': cred})
        code = pg_response['code']
        if code:
            self.logger.error("Received error code: %d", code)
            output = pg_response['output']
            self.logger.error("Received error message: %s", output)
            # Return an empty list.
            return list()
        # value is a list of dicts, each containing info about an aggregate
        return pg_response['value']
    
    def _find_geni_ams(self, cm_dicts):
        """Finds ComponentManagers that also support the GENI AM API.
        Returns a list of dicts containing those CMs that implement the AM API.
        The AM URL is included in the dict in the key 'am_url'.
        """
        result = list()
        for cm_dict in cm_dicts:
            cm_url = cm_dict['url']
            self.logger.debug('Checking for AM at %s', cm_url)
            am_url = self._cm_to_am(cm_url)
            self.logger.debug('AM URL = %s', am_url)
            if am_url != cm_url:
                # Test the am_url...
                client = make_client(am_url, self.config['key'],
                                     self.config['cert'],
                                     self.config['verbose'],
                                     timeout=5)
                try:
                    version = client.GetVersion()
                    self.logger.debug('version = %r', version)
                    # Temporarily accept pg style result until pgeni3 is upgraded.
                    if version.has_key('output'):
                        version = version['value']
                    if version.has_key('geni_api'):
                        cm_dict['am_url'] = am_url
                        result.append(cm_dict)
                except xmlrpclib.ProtocolError, err:
                    self.logger.debug("Skipping %s due to xml rpc error: %s",
                                      cm_url, err)
                except ssl.SSLError, err:
                    self.logger.debug("Skipping %s due to ssl error: %s",
                                      cm_url, err)
                except socket.error, err:
                    self.logger.debug("Skipping %s due to socket error: %s",
                                      cm_url, err)
        return result

    def _cm_to_am(self, url):
        """Convert a CM url to an AM url."""
        # Replace the trailing "cm" with "am"
        if url.endswith('cm'):
            return url[:-2] + 'am'
        else:
            return url
