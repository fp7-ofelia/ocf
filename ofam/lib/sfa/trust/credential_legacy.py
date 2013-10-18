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
# Implements SFA Credentials
#
# Credentials are layered on top of certificates, and are essentially a
# certificate that stores a tuple of parameters.
##

### $Id: credential.py 17477 2010-03-25 16:49:34Z jkarlin $
### $URL: svn+ssh://svn.planet-lab.org/svn/sfa/branches/geni-api/sfa/trust/credential.py $

import xmlrpclib

from sfa.util.faults import *
from sfa.trust.certificate import Certificate
from sfa.trust.rights import Right,Rights
from sfa.trust.gid import GID

##
# Credential is a tuple:
#     (GIDCaller, GIDObject, LifeTime, Privileges, Delegate)
#
# These fields are encoded using xmlrpc into the subjectAltName field of the
# x509 certificate. Note: Call encode() once the fields have been filled in
# to perform this encoding.

class CredentialLegacy(Certificate):
    gidCaller = None
    gidObject = None
    lifeTime = None
    privileges = None
    delegate = False

    ##
    # Create a Credential object
    #
    # @param create If true, create a blank x509 certificate
    # @param subject If subject!=None, create an x509 cert with the subject name
    # @param string If string!=None, load the credential from the string
    # @param filename If filename!=None, load the credential from the file

    def __init__(self, create=False, subject=None, string=None, filename=None):
        Certificate.__init__(self, create, subject, string, filename)

    ##
    # set the GID of the caller
    #
    # @param gid GID object of the caller

    def set_gid_caller(self, gid):
        self.gidCaller = gid
        # gid origin caller is the caller's gid by default
        self.gidOriginCaller = gid

    ##
    # get the GID of the object

    def get_gid_caller(self):
        if not self.gidCaller:
            self.decode()
        return self.gidCaller

    ##
    # set the GID of the object
    #
    # @param gid GID object of the object

    def set_gid_object(self, gid):
        self.gidObject = gid

    ##
    # get the GID of the object

    def get_gid_object(self):
        if not self.gidObject:
            self.decode()
        return self.gidObject

    ##
    # set the lifetime of this credential
    #
    # @param lifetime lifetime of credential

    def set_lifetime(self, lifeTime):
        self.lifeTime = lifeTime

    ##
    # get the lifetime of the credential

    def get_lifetime(self):
        if not self.lifeTime:
            self.decode()
        return self.lifeTime

    ##
    # set the delegate bit
    #
    # @param delegate boolean (True or False)

    def set_delegate(self, delegate):
        self.delegate = delegate

    ##
    # get the delegate bit

    def get_delegate(self):
        if not self.delegate:
            self.decode()
        return self.delegate

    ##
    # set the privileges
    #
    # @param privs either a comma-separated list of privileges of a Rights object

    def set_privileges(self, privs):
        if isinstance(privs, str):
            self.privileges = Rights(string = privs)
        else:
            self.privileges = privs

    ##
    # return the privileges as a Rights object

    def get_privileges(self):
        if not self.privileges:
            self.decode()
        return self.privileges

    ##
    # determine whether the credential allows a particular operation to be
    # performed
    #
    # @param op_name string specifying name of operation ("lookup", "update", etc)

    def can_perform(self, op_name):
        rights = self.get_privileges()
        if not rights:
            return False
        return rights.can_perform(op_name)

    ##
    # Encode the attributes of the credential into a string and store that
    # string in the alt-subject-name field of the X509 object. This should be
    # done immediately before signing the credential.

    def encode(self):
        dict = {"gidCaller": None,
                "gidObject": None,
                "lifeTime": self.lifeTime,
                "privileges": None,
                "delegate": self.delegate}
        if self.gidCaller:
            dict["gidCaller"] = self.gidCaller.save_to_string(save_parents=True)
        if self.gidObject:
            dict["gidObject"] = self.gidObject.save_to_string(save_parents=True)
        if self.privileges:
            dict["privileges"] = self.privileges.save_to_string()
        str = xmlrpclib.dumps((dict,), allow_none=True)
        self.set_data('URI:http://' + str)

    ##
    # Retrieve the attributes of the credential from the alt-subject-name field
    # of the X509 certificate. This is automatically done by the various
    # get_* methods of this class and should not need to be called explicitly.

    def decode(self):
        data = self.get_data().lstrip('URI:http://')
        
        if data:
            dict = xmlrpclib.loads(data)[0][0]
        else:
            dict = {}

        self.lifeTime = dict.get("lifeTime", None)
        self.delegate = dict.get("delegate", None)

        privStr = dict.get("privileges", None)
        if privStr:
            self.privileges = Rights(string = privStr)
        else:
            self.privileges = None

        gidCallerStr = dict.get("gidCaller", None)
        if gidCallerStr:
            self.gidCaller = GID(string=gidCallerStr)
        else:
            self.gidCaller = None

        gidObjectStr = dict.get("gidObject", None)
        if gidObjectStr:
            self.gidObject = GID(string=gidObjectStr)
        else:
            self.gidObject = None

    ##
    # Verify that a chain of credentials is valid (see cert.py:verify). In
    # addition to the checks for ordinary certificates, verification also
    # ensures that the delegate bit was set by each parent in the chain. If
    # a delegate bit was not set, then an exception is thrown.
    #
    # Each credential must be a subset of the rights of the parent.

    def verify_chain(self, trusted_certs = None):
        # do the normal certificate verification stuff
        Certificate.verify_chain(self, trusted_certs)

        if self.parent:
            # make sure the parent delegated rights to the child
            if not self.parent.get_delegate():
                raise MissingDelegateBit(self.parent.get_subject())

            # make sure the rights given to the child are a subset of the
            # parents rights
            if not self.parent.get_privileges().is_superset(self.get_privileges()):
                raise ChildRightsNotSubsetOfParent(self.get_subject() 
                                                   + " " + self.parent.get_privileges().save_to_string()
                                                   + " " + self.get_privileges().save_to_string())

        return

    ##
    # Dump the contents of a credential to stdout in human-readable format
    #
    # @param dump_parents If true, also dump the parent certificates

    def dump(self, *args, **kwargs):
        print self.dump_string(*args,**kwargs)

    def dump_string(self, dump_parents=False):
        result=""
        result += "CREDENTIAL %s\n" % self.get_subject()

        result += "      privs: %s\n" % self.get_privileges().save_to_string()

        gidCaller = self.get_gid_caller()
        if gidCaller:
            result += "  gidCaller:\n"
            gidCaller.dump(8, dump_parents)

        gidObject = self.get_gid_object()
        if gidObject:
            result += "  gidObject:\n"
            result += gidObject.dump_string(8, dump_parents)

        result += "   delegate: %s" % self.get_delegate()

        if self.parent and dump_parents:
            result += "PARENT\n"
            result += self.parent.dump_string(dump_parents)

        return result
