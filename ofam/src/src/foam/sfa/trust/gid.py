#----------------------------------------------------------------------
# Copyright (c) 2008 Board of Trustees, Princeton University
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
##
# Implements SFA GID. GIDs are based on certificates, and the GID class is a
# descendant of the certificate class.
##

import xmlrpclib
import uuid

from foam.sfa.trust.certificate import Certificate

from foam.sfa.util.faults import GidInvalidParentHrn, GidParentHrn
#from foam.sfa.util.foam.sfa.ogging import logger
from foam.sfa.util.xrn import hrn_to_urn, urn_to_hrn, hrn_authfor_hrn

##
# Create a new uuid. Returns the UUID as a string.

def create_uuid():
    return str(uuid.uuid4().int)

##
# GID is a tuple:
#    (uuid, urn, public_key)
#
# UUID is a unique identifier and is created by the python uuid module
#    (or the utility function create_uuid() in gid.py).
#
# HRN is a human readable name. It is a dotted form similar to a backward domain
#    name. For example, planetlab.us.arizona.bakers.
#
# URN is a human readable identifier of form:
#   "urn:publicid:IDN+toplevelauthority[:sub-auth.]*[\res. type]\ +object name"
#   For  example, urn:publicid:IDN+planetlab:us:arizona+user+bakers      
#
# PUBLIC_KEY is the public key of the principal identified by the UUID/HRN.
# It is a Keypair object as defined in the cert.py module.
#
# It is expected that there is a one-to-one pairing between UUIDs and HRN,
# but it is uncertain how this would be inforced or if it needs to be enforced.
#
# These fields are encoded using xmlrpc into the subjectAltName field of the
# x509 certificate. Note: Call encode() once the fields have been filled in
# to perform this encoding.


class GID(Certificate):
    ##
    # Create a new GID object
    #
    # @param create If true, create the X509 certificate
    # @param subject If subject!=None, create the X509 cert and set the subject name
    # @param string If string!=None, load the GID from a string
    # @param filename If filename!=None, load the GID from a file
    # @param lifeDays life of GID in days - default is 1825==5 years

    def __init__(self, create=False, subject=None, string=None, filename=None, uuid=None, hrn=None, urn=None, lifeDays=1825, email=None):
        self.uuid = None
        self.hrn = None
        self.urn = None
        self.email = None # for adding to the SubjectAltName
        Certificate.__init__(self, lifeDays, create, subject, string, filename)
        
        if subject:
            print "Creating GID for subject: %s" % subject
        if uuid:
            self.uuid = int(uuid)
        if hrn:
            self.hrn = hrn
            self.urn = hrn_to_urn(hrn, 'unknown')
        if urn:
            self.urn = urn
            self.hrn, type = urn_to_hrn(urn)
        if email:
            self.set_email(email) 

    def set_uuid(self, uuid):
        if isinstance(uuid, str):
            self.uuid = int(uuid)
        else:
            self.uuid = uuid

    def get_uuid(self):
        if not self.uuid:
            self.decode()
        return self.uuid

    def set_hrn(self, hrn):
        self.hrn = hrn

    def get_hrn(self):
        if not self.hrn:
            self.decode()
        return self.hrn

    def set_urn(self, urn):
        self.urn = urn
        self.hrn, type = urn_to_hrn(urn)
 
    def get_urn(self):
        if not self.urn:
            self.decode()
        return self.urn            

    # Will be stuffed into subjectAltName
    def set_email(self, email):
        self.email = email

    def get_email(self):
        if not self.email:
            self.decode()
        return self.email

    def get_type(self):
        if not self.urn:
            self.decode()
        _, t = urn_to_hrn(self.urn)
        return t
    
    ##
    # Encode the GID fields and package them into the subject-alt-name field
    # of the X509 certificate. This must be called prior to signing the
    # certificate. It may only be called once per certificate.

    def encode(self):
        if self.urn:
            urn = self.urn
        else:
            urn = hrn_to_urn(self.hrn, None)
            
        str = "URI:" + urn

        if self.uuid:
            str += ", " + "URI:" + uuid.UUID(int=self.uuid).urn
        
        if self.email:
            str += ", " + "email:" + self.email

        self.set_data(str, 'subjectAltName')


    ##
    # Decode the subject-alt-name field of the X509 certificate into the
    # fields of the GID. This is automatically called by the various get_*()
    # functions in this class.

    def decode(self):
        data = self.get_data('subjectAltName')
        dict = {}
        if data:
            if data.lower().startswith('uri:http://<params>'):
                dict = xmlrpclib.loads(data[11:])[0][0]
            else:
                spl = data.split(', ')
                for val in spl:
                    if val.lower().startswith('uri:urn:uuid:'):
                        dict['uuid'] = uuid.UUID(val[4:]).int
                    elif val.lower().startswith('uri:urn:publicid:idn+'):
                        dict['urn'] = val[4:]
                    elif val.lower().startswith('email:'):
                        # FIXME: Ensure there isn't cruft in that address...
                        # EG look for email:copy,....
                        dict['email'] = val[6:]
                    
        self.uuid = dict.get("uuid", None)
        self.urn = dict.get("urn", None)
        self.hrn = dict.get("hrn", None)
        self.email = dict.get("email", None)
        if self.urn:
            self.hrn = urn_to_hrn(self.urn)[0]

    ##
    # Dump the credential to stdout.
    #
    # @param indent specifies a number of spaces to indent the output
    # @param dump_parents If true, also dump the parents of the GID

    def dump(self, *args, **kwargs):
        print self.dump_string(*args,**kwargs)

    def dump_string(self, indent=0, dump_parents=False):
        result=" "*(indent-2) + "GID\n"
        result += " "*indent + "hrn:" + str(self.get_hrn()) +"\n"
        result += " "*indent + "urn:" + str(self.get_urn()) +"\n"
        result += " "*indent + "uuid:" + str(self.get_uuid()) + "\n"
        if self.get_email() is not None:
            result += " "*indent + "email:" + str(self.get_email()) + "\n"
        filename=self.get_filename()
        if filename: result += "Filename %s\n"%filename

        if self.parent and dump_parents:
            result += " "*indent + "parent:\n"
            result += self.parent.dump_string(indent+4, dump_parents)
        return result

    ##
    # Verify the chain of authenticity of the GID. First perform the checks
    # of the certificate class (verifying that each parent signs the child,
    # etc). In addition, GIDs also confirm that the parent's HRN is a prefix
    # of the child's HRN, and the parent is of type 'authority'.
    #
    # Verifying these prefixes prevents a rogue authority from signing a GID
    # for a principal that is not a member of that authority. For example,
    # planetlab.us.arizona cannot sign a GID for planetlab.us.princeton.foo.

    def verify_chain(self, trusted_certs = None):
        # do the normal certificate verification stuff
        trusted_root = Certificate.verify_chain(self, trusted_certs)        
       
        if self.parent:
            # make sure the parent's hrn is a prefix of the child's hrn
            if not hrn_authfor_hrn(self.parent.get_hrn(), self.get_hrn()):
                raise GidParentHrn("This cert HRN %s isn't in the namespace for parent HRN %s" % (self.get_hrn(), self.parent.get_hrn()))

            # Parent must also be an authority (of some type) to sign a GID
            # There are multiple types of authority - accept them all here
            if not self.parent.get_type().find('authority') == 0:
                raise GidInvalidParentHrn("This cert %s's parent %s is not an authority (is a %s)" % (self.get_hrn(), self.parent.get_hrn(), self.parent.get_type()))

            # Then recurse up the chain - ensure the parent is a trusted
            # root or is in the namespace of a trusted root
            self.parent.verify_chain(trusted_certs)
        else:
            # make sure that the trusted root's hrn is a prefix of the child's
            trusted_gid = GID(string=trusted_root.save_to_string())
            trusted_type = trusted_gid.get_type()
            trusted_hrn = trusted_gid.get_hrn()
            #if trusted_type == 'authority':
            #    trusted_hrn = trusted_hrn[:trusted_hrn.rindex('.')]
            cur_hrn = self.get_hrn()
            if not hrn_authfor_hrn(trusted_hrn, cur_hrn):
                raise GidParentHrn("Trusted root with HRN %s isn't a namespace authority for this cert: %s" % (trusted_hrn, cur_hrn))

            # There are multiple types of authority - accept them all here
            if not trusted_type.find('authority') == 0:
                raise GidInvalidParentHrn("This cert %s's trusted root signer %s is not an authority (is a %s)" % (self.get_hrn(), trusted_hrn, trusted_type))

        return
