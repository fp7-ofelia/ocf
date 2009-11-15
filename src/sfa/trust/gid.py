##
# Implements GENI GID. GIDs are based on certificates, and the GID class is a
# descendant of the certificate class.
##

### $Id: gid.py 14420 2009-07-09 17:18:07Z thierry $
### $URL: http://svn.planet-lab.org/svn/sfa/tags/sfa-0.9-5/sfa/trust/gid.py $

import xmlrpclib
import uuid

from sfa.trust.certificate import Certificate

##
# Create a new uuid. Returns the UUID as a string.

def create_uuid():
    return str(uuid.uuid4().int)

##
# GID is a tuplie:
#    (uuid, hrn, public_key)
#
# UUID is a unique identifier and is created by the python uuid module
#    (or the utility function create_uuid() in gid.py).
#
# HRN is a human readable name. It is a dotted form similar to a backward domain
#    name. For example, planetlab.us.arizona.bakers.
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
    uuid = None
    hrn = None

    ##
    # Create a new GID object
    #
    # @param create If true, create the X509 certificate
    # @param subject If subject!=None, create the X509 cert and set the subject name
    # @param string If string!=None, load the GID from a string
    # @param filename If filename!=None, load the GID from a file

    def __init__(self, create=False, subject=None, string=None, filename=None, uuid=None, hrn=None):
        Certificate.__init__(self, create, subject, string, filename)
        if uuid:
            self.uuid = uuid
        if hrn:
            self.hrn = hrn

    def set_uuid(self, uuid):
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

    ##
    # Encode the GID fields and package them into the subject-alt-name field
    # of the X509 certificate. This must be called prior to signing the
    # certificate. It may only be called once per certificate.

    def encode(self):
        dict = {"uuid": self.uuid,
                "hrn": self.hrn}
        str = xmlrpclib.dumps((dict,))
        self.set_data(str)

    ##
    # Decode the subject-alt-name field of the X509 certificate into the
    # fields of the GID. This is automatically called by the various get_*()
    # functions in this class.

    def decode(self):
        data = self.get_data()
        if data:
            dict = xmlrpclib.loads(self.get_data())[0][0]
        else:
            dict = {}

        self.uuid = dict.get("uuid", None)
        self.hrn = dict.get("hrn", None)

    ##
    # Dump the credential to stdout.
    #
    # @param indent specifies a number of spaces to indent the output
    # @param dump_parents If true, also dump the parents of the GID

    def dump(self, indent=0, dump_parents=False):
        print " "*indent, " hrn:", self.get_hrn()
        print " "*indent, "uuid:", self.get_uuid()

        if self.parent and dump_parents:
            print " "*indent, "parent:"
            self.parent.dump(indent+4)

    ##
    # Verify the chain of authenticity of the GID. First perform the checks
    # of the certificate class (verifying that each parent signs the child,
    # etc). In addition, GIDs also confirm that the parent's HRN is a prefix
    # of the child's HRN.
    #
    # Verifying these prefixes prevents a rogue authority from signing a GID
    # for a principal that is not a member of that authority. For example,
    # planetlab.us.arizona cannot sign a GID for planetlab.us.princeton.foo.

    def verify_chain(self, trusted_certs = None):
        # do the normal certificate verification stuff
        Certificate.verify_chain(self, trusted_certs)

        if self.parent:
            # make sure the parent's hrn is a prefix of the child's hrn
            if not self.get_hrn().startswith(self.parent.get_hrn()):
                raise GidParentHrn(self.parent.get_subject())

        return





