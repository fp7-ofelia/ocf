import xmlrpclib

from BaseApi import BaseApi

from sfa.trust.credential import Credential
from sfa.trust.gid import GID
from sfa.trust.trustedroot import TrustedRootList

from ApiExceptionCodes import *

class BadRequestHash(xmlrpclib.Fault):
   def __init__(self, hash = None):
        faultString = "bad request hash: " + str(hash)
        xmlrpclib.Fault.__init__(self, FAULT_BADREQUESTHASH, faultString)

class AuthenticatedApi(BaseApi):
    def __init__(self, encoding = "utf-8", trustedRootsDir=None):
        BaseApi.__init__(self, encoding)
        if trustedRootsDir:
            self.trusted_cert_list = TrustedRootList(trustedRootsDir).get_list()
        else:
            self.trusted_cert_list = None

    def register_functions(self):
        BaseApi.register_functions(self)
        self.register_function(self.gidNoop)

    def verifyGidRequestHash(self, gid, hash, arglist):
        key = gid.get_pubkey()
        if not key.verify_string(str(arglist), hash):
            raise BadRequestHash(hash)

    def verifyCredRequestHash(self, cred, hash, arglist):
        gid = cred.get_gid_caller()
        self.verifyGidRequestHash(gid, hash, arglist)

    def validateGid(self, gid):
        if self.trusted_cert_list:
            gid.verify_chain(self.trusted_cert_list)

    def validateCred(self, cred):
        if self.trusted_cert_list:
            cred.verify_chain(self.trusted_cert_list)
            caller_gid = cred.get_gid_caller()
            object_gid = cred.get_gid_object()
            if caller_gid:
                caller_gid.verify_chain(self.trusted_cert_list)
            if object_gid:
                object_gid.verify_chain(self.trusted_cert_list)

    def authenticateGid(self, gidStr, argList, requestHash):
        gid = GID(string = gidStr)
        self.validateGid(gid)
        self.verifyGidRequestHash(gid, requestHash, argList)
        return gid

    def authenticateCred(self, credStr, argList, requestHash):
        cred = Credential(string = credStr)
        self.validateCred(cred)
        self.verifyCredRequestHash(cred, requestHash, argList)
        return cred

    def gidNoop(self, gidStr, value, requestHash):
        self.authenticateGid(gidStr, [gidStr, value], requestHash)
        return value

    def credNoop(self, credStr, value, requestHash):
        self.authenticateCred(credStr, [credStr, value], requestHash)
        return value


