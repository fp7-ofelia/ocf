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
import logging
import os
import time
import sys


# FIXME: Use the constant from namespace
URN_PREFIX = "urn:publicid:IDN"

# FIXME: Use sfa util code!
def urn_to_hrn(urn):
    """
    convert a urn to hrn
    return a tuple (hrn, type)
    """

    # if this is already a hrn dont do anything
    if not urn or not urn.startswith(URN_PREFIX):
        return urn, None

    name = urn[len(URN_PREFIX):]
    hrn_parts = name.split("+")
    
    # type is always the second to last element in the list
    type = hrn_parts.pop(-2)

    # convert hrn_parts (list) into hrn (str) by doing the following    
    # remove blank elements
    # replace ':' with '.'
    # join list elements using '.'
    hrn = '.'.join([part.replace(':', '.') for part in hrn_parts if part]) 
   
    return str(hrn), str(type) 

def get_authority(xrn):
    hrn, type = urn_to_hrn(xrn)
    if type and type == 'authority':
        return hrn
    
    parts = hrn.split(".")
    return ".".join(parts[:-1])

def get_leaf(hrn):
    parts = hrn.split(".")
    return ".".join(parts[-1:])

def hrn_to_urn(hrn, type=None):
    """
    convert an hrn and type to a urn string
    """
    # if  this is already a urn dont do anything 
    if not hrn or hrn.startswith(URN_PREFIX):
        return hrn

    authority = get_authority(hrn)
    name = get_leaf(hrn)
    
    if authority.startswith("plc"):
        if type == None:
            urn = "+".join(['',authority.replace('.',':'),name])
        else:
            urn = "+".join(['',authority.replace('.',':'),type,name])

    else:
        urn = "+".join(['',authority,type,name])
        
    return URN_PREFIX + urn

def create_selfsigned_cert2(filename, user, key):
    """ Creates a self-signed cert with CN of issuer and subject = user.
    The file is stored in 'filename' and the public/private key is found in key """
    
    from OpenSSL import crypto
    # Create a self-signed cert to talk to the registry with
    cert = crypto.X509()
    cert.set_serial_number(3)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(60*60*24*365*5) # five years

    req = crypto.X509Req()
    subj = req.get_subject()
    setattr(subj, "CN", user)
    cert.set_subject(subj)
    
    key = crypto.load_privatekey(crypto.FILETYPE_PEM, file(key).read())
    cert.set_pubkey(key)

    cert.set_issuer(subj)
    cert.sign(key, "md5")
    
        
    f = open(filename,'w')
    f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    f.close()
    

def create_selfsigned_cert(filename, user, key):
    config = """[ req ]
            distinguished_name = req_distinguished_name
            attributes = req_attributes
            prompt = no
            
            [ req_distinguished_name ]
            C = US
            ST = .
            L = .
            O = GENI
            OU = GENI
            CN = %s
            emailAddress = .
            
            [ req_attributes ]
            unstructuredName =""" % user
    
    f = open("/tmp/tmp_openssl_config",'w')
    f.write(config)
    f.close()
    os.popen('openssl req -new -x509 -nodes -sha1 -config /tmp/tmp_openssl_config -key %s > %s' % (key, filename))
    os.remove("/tmp/tmp_openssl_config")
    

class Framework(Framework_Base):
    def __init__(self, config):
        config['cert'] = os.path.expanduser(config['cert'])
        config['key'] = os.path.expanduser(config['key'])        

        self.config = config

        # Download a cert from PLC if necessary
        if not os.path.exists(config['cert']):
            res = raw_input("Your certificate file (%s) was not found, would you like me to download it for you to %s? (Y/n)" % (config['cert'],config['cert']))
            if not res.lower().startswith('n'):
                # Create a self-signed cert to talk to the registry with
                create_selfsigned_cert2(config['cert'], config['user'], config['key'])
                try:
                    # use the self signed cert to get the gid
                    self.registry = make_client(config['registry'], config['key'], config['cert'])
                    self.user_cred = None
                    self.cert_string = file(config['cert'],'r').read()
                    cred = self.get_user_cred()
                    gid = self.registry.Resolve(config['user'], cred)[0]['gid']
                    # Finally, copy the gid to the cert location
                    f = open(self.config['cert'],'w')
                    f.write(gid)
                    f.close()
                except Exception, exc:
                    os.remove(self.config['cert'])
                    sys.exit("Failed to download a user certificate from the PL registry: %s" % exc)
            else:            
                sys.exit("SFA Framework certfile %s doesn't exist" % config['cert'])
                
                
        if not os.path.exists(config['key']):
            sys.exit('SFA Framework keyfile %s doesnt exist' % config['key'])
        if not config.has_key('verbose'):
            config['verbose'] = False
        logger = logging.getLogger('omni.sfa')
        logger.info('SFA Registry: %s', config['registry'])
        self.registry = make_client(config['registry'], config['key'], config['cert'], allow_none=True)
        logger.info('SFA Slice Manager: %s', config['slicemgr'])
        self.slicemgr = make_client(config['slicemgr'], config['key'], config['cert'])
        self.cert_string = file(config['cert'],'r').read()
        self.user_cred = None
        
    def get_user_cred(self):
        if self.user_cred is None:
            try:
                self.user_cred = self.registry.get_self_credential(self.cert_string, "user", self.config['user'])
            except Exception as exc:
                raise Exception("Using SFA Failed to get User credentials from registry %s cert file %s, user %s: %s" % (self.config['registry'], self.config['cert'], self.config['user'], exc))
        return self.user_cred
    
    def get_slice_cred(self, urn):
        user_cred = self.get_user_cred()
        return self.registry.get_credential(user_cred, 'slice', urn)
    
    def create_slice(self, urn):    
        ''' Gets the credential for a slice, creating the slice 
            if it doesn't already exist
        '''
        hrn, type = urn_to_hrn(urn)

        try:
            slice_cred = self.get_slice_cred(urn)
        except:
            # Slice doesn't exist, create it
            user_cred = self.get_user_cred()
            auth_cred = self.registry.get_credential(user_cred, "authority", self.config['authority'])
            # Note this is in UTC
            expiration = int(time.time()) + 60 * 60 * 24
            authority = self.config['authority']
            user = self.config['user']
                           
            record = {'peer_authority': '', u'description': u'a slice', u'url': \
                      u'http://www.testslice.com', u'expires': u'%s' % expiration, \
                      u'authority': u'%s' % authority, u'researcher': [u'%s' % user], \
                      'hrn': u'%s' % hrn, u'PI': [u'%s' % user], 'type': u'slice', \
                      u'name': u'%s' % hrn}
    
            self.registry.register(auth_cred, record)
            slice_cred = self.get_slice_cred(urn)

        return slice_cred
        
    
    def delete_slice(self, urn):
        ''' Deletes the slice '''
        user_cred = self.get_user_cred()
        auth_cred = self.registry.get_credential(user_cred, "authority", self.config['authority'])
     
        return self.registry.remove(auth_cred, 'slice', urn)
 
    def renew_slice(self, urn, requested_expiration):
        """Renew a slice.
        
        urn is framework urn, already converted via slice_name_to_urn.
        requested_expiration is a datetime object.
        
        Returns the expiration date as a datetime. If there is an error,
        print it and return None.
        """
        slice_cred = self.get_slice_cred(urn)
        user_cred = self.get_user_cred()
        try:
            slice_record = self.registry.Resolve(urn, user_cred)[0]
            slice_record['expires'] = int(time.mktime(requested_expiration.timetuple()))
            res = self.registry.Update(slice_record, slice_cred)
            if res == 1:
                return requested_expiration
            else:
                self.logger.warning("Failed to renew slice %s" % urn)

        except Exception, exc:
            self.logger.warning("Failed to renew slice %s: %s" % urn, exc)
            return None            
       
    def list_aggregates(self):
        user_cred = self.get_user_cred()
        sites = self.registry.get_aggregates(user_cred)
        aggs = {}
        for site in sites:
            aggs[site['urn']] = site['url']

        return aggs


    def slice_name_to_urn(self, name):
        """Convert a slice name to a slice urn."""
        # FIXME: Use constant from SFA util code
        # FIXME: use something like credential.publicid_to_urn
        base = 'urn:publicid:IDN+'
        auth = self.config['authority'].replace('.',':')

        if name.startswith(base):
            if not name.startswith(base+auth+"+slice+"):
                raise Exception("Incorrect slice name")
            return name
        
        if name.startswith(auth):
            return base + name

        if '+' in name:
            raise Exception("Incorrect slice name")
                            
        return base + auth + "+slice+" + name
        
