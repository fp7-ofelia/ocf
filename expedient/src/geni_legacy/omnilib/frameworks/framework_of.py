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
from omnilib.xmlrpc.client import make_client
from omnilib.frameworks.framework_base import Framework_Base
import os
import traceback
import sys
import time

class Framework(Framework_Base):
    def __init__(self, config):
        config['cert'] = os.path.expanduser(config['cert'])
        if not os.path.exists(config['cert']):
            sys.exit('OpenFlow Framework certfile %s doesnt exist' % config['cert'])
        config['key'] = os.path.expanduser(config['key'])        
        if not os.path.exists(config['key']):
            sys.exit('OpenFlow Framework keyfile %s doesnt exist' % config['key'])
        if not config.has_key('verbose'):
            config['verbose'] = False
        self.config = config
        
        self.ch = make_client(config['ch'], config['key'], config['cert'])
        self.cert_string = file(config['cert'],'r').read()
        self.user_cred = None
        
    def get_user_cred(self):
        if self.user_cred == None:
            try:
                self.user_cred = self.ch.CreateUserCredential(self.cert_string)
            except Exception:
                raise Exception("Using OpenFlow Failed to do CH.CreateUserCredentials on CH %s from cert file %s: %s" % (self.config['ch'], self.config['cert'], traceback.format_exc()))
        return self.user_cred
    
    def get_slice_cred(self, urn):
        return self.ch.CreateSlice(urn)
    
    def create_slice(self, urn):    
        return self.get_slice_cred(urn)
    
    def delete_slice(self, urn):
        return self.ch.DeleteSlice(urn)
     
    def list_aggregates(self):
        sites = []
        try:
            sites = self.ch.ListAggregates()
        except Exception:
            raise Exception("Using OpenFlow Failed to do CH.ListAggregates on CH %s from cert file %s: %s" % (self.config['ch'], self.config['cert'], traceback.format_exc()))
        aggs = {}
        for (urn, url) in sites:
            aggs[urn] = url
        
        return aggs

    
    def slice_name_to_urn(self, name):
        """Convert a slice name to a slice urn."""
        # FIXME: Use constants
        base = 'urn:publicid:IDN+'
        # FIXME: Validate name from credential.publicid_to_urn

        # Old OMNI configs did not have authority specified,
        # all we can do with those is append the name to the base        
        if not self.config.has_key('authority'):
            if name.startswith(base):
                return name
            else:
                return base + name
        
        auth = self.config['authority']

        if name.startswith(base):
            if not name.startswith(base+auth+"+slice+"):
                raise Exception("Incorrect slice name")
            return name
        
        if name.startswith(auth):
            return base + name

        if '+' in name:
            raise Exception("Incorrect slice name")
                            
        return base + auth + "+slice+" + name

    def renew_slice(self, urn, expiration_dt):
        """See framework_base for doc.
        """
        expiration = expiration_dt.isoformat()
        if self.ch.RenewSlice(urn, expiration):
            return expiration_dt
        else:
            return None
