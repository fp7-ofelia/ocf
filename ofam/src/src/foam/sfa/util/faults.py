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
#
# SFA API faults
#

import xmlrpclib
from foam.sfa.util.genicode import GENICODE

class SfaFault(xmlrpclib.Fault):
    def __init__(self, faultCode, faultString, extra = None):
        if extra:
            faultString += ": " + str(extra)
        xmlrpclib.Fault.__init__(self, faultCode, faultString)

class OCFSfaPermissionDenied(SfaFault):
    def __init__(self,value='',extra = None):
        self.faultString = "Permission denied: %s" % value
        self.code = GENICODE.FORBIDDEN
        SfaFault.__init__(self, self.code, self.faultString, extra)

class OCFSfaError(SfaFault):
    def __init__(self,value='',method='',extra = None):
        self.faultString = "Error in method %s %s" % (method, value) 
        self.code = GENICODE.ERROR
        SfaFault.__init__(self, self.code, self.faultString, extra)

class SfaInvalidAPIMethod(SfaFault):
    def __init__(self, method, interface = None, extra = None):
        faultString = "Invalid method " + method
        if interface:
            faultString += " for interface " + interface
        SfaFault.__init__(self, GENICODE.UNSUPPORTED, faultString, extra)

class SfaInvalidArgumentCount(SfaFault):
    def __init__(self, got, min, max = min, extra = None):
        if min != max:
            expected = "%d-%d" % (min, max)
        else:
            expected = "%d" % min
        faultString = "Expected %s arguments, got %d" % \
                      (expected, got)
        SfaFault.__init__(self, GENICODE.BADARGS, faultString, extra)

class SfaInvalidArgument(SfaFault):
    def __init__(self, extra = None, name = None):
        if name is not None:
            faultString = "Invalid %s value" % name
        else:
            faultString = "Invalid argument"
        SfaFault.__init__(self, GENICODE.BADARGS, faultString, extra)

class SfaAuthenticationFailure(SfaFault):
    def __init__(self, extra = None):
        faultString = "Failed to authenticate call"
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)

class SfaDBError(SfaFault):
    def __init__(self, extra = None):
        faultString = "Database error"
        SfaFault.__init__(self, GENICODE.DBERROR, faultString, extra)

class SfaPermissionDenied(SfaFault):
    def __init__(self, extra = None):
        faultString = "Permission denied"
        SfaFault.__init__(self, GENICODE.FORBIDDEN, faultString, extra)

class SfaNotImplemented(SfaFault):
    def __init__(self, interface=None, extra = None):
        faultString = "Not implemented"
        if interface:
            faultString += " at interface " + interface 
        SfaFault.__init__(self, GENICODE.UNSUPPORTED, faultString, extra)

class SfaAPIError(SfaFault):
    def __init__(self, extra = None):
        faultString = "Internal API error"
        SfaFault.__init__(self, GENICODE.SERVERERROR, faultString, extra)

class MalformedHrnException(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Malformed HRN: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, extra)
    def __str__(self):
        return repr(self.value)

class TreeException(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Tree Exception: %(value)s, " % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)

class NonExistingRecord(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Non exsiting record %(value)s, " % locals()
        SfaFault.__init__(self, GENICODE.SEARCHFAILED, faultString, extra)
    def __str__(self):
        return repr(self.value)

class ExistingRecord(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Existing record: %(value)s, " % locals()
        SfaFault.__init__(self, GENICODE.REFUSED, faultString, extra)
    def __str__(self):
        return repr(self.value)

    
class InvalidRPCParams(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Invalid RPC Params: %(value)s, " % locals()
        SfaFault.__init__(self, GENICODE.RPCERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)

# SMBAKER exceptions follow

class ConnectionKeyGIDMismatch(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Connection Key GID mismatch: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra) 
    def __str__(self):
        return repr(self.value)

class MissingCallerGID(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Missing Caller GID: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra) 
    def __str__(self):
        return repr(self.value)

class RecordNotFound(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Record not found: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)

class UnknownSfaType(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Unknown SFA Type: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)

class MissingAuthority(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Missing authority: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)

class PlanetLabRecordDoesNotExist(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "PlanetLab record does not exist : %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)

class PermissionError(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Permission error: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.FORBIDDEN, faultString, extra)
    def __str__(self):
        return repr(self.value)

class InsufficientRights(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Insufficient rights: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.FORBIDDEN, faultString, extra)
    def __str__(self):
        return repr(self.value)

class MissingDelegateBit(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Missing delegate bit: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.FORBIDDEN, faultString, extra)
    def __str__(self):
        return repr(self.value)

class ChildRightsNotSubsetOfParent(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Child rights not subset of parent: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.FORBIDDEN, faultString, extra)
    def __str__(self):
        return repr(self.value)

class CertMissingParent(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Cert missing parent: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)

class CertNotSignedByParent(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Cert not signed by parent: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)
    
class GidParentHrn(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Cert URN is not an extension of its parent: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)
        
class GidInvalidParentHrn(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "GID invalid parent hrn: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)

class SliverDoesNotExist(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Sliver does not exist : %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)

class BadRequestHash(xmlrpclib.Fault):
    def __init__(self, hash = None, extra = None):
        faultString = "bad request hash: " + str(hash)
        xmlrpclib.Fault.__init__(self, GENICODE.ERROR, faultString)

class MissingTrustedRoots(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Trusted root directory does not exist: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.SERVERERROR, faultString, extra) 
    def __str__(self):
        return repr(self.value)

class MissingSfaInfo(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Missing information: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra) 
    def __str__(self):
        return repr(self.value)

class InvalidRSpec(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Invalid RSpec: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)

class InvalidRSpecVersion(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Invalid RSpec version: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.BADVERSION, faultString, extra)
    def __str__(self):
        return repr(self.value)

class UnsupportedRSpecVersion(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Unsupported RSpec version: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.UNSUPPORTED, faultString, extra)
    def __str__(self):
        return repr(self.value)

class InvalidRSpecElement(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Invalid RSpec Element: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)

class InvalidXML(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Invalid XML Document: %(value)s" % locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)

class AccountNotEnabled(SfaFault):
    def __init__(self,  extra = None):
        faultString = "Account Disabled"
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)

class CredentialNotVerifiable(SfaFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Unable to verify credential: %(value)s, " %locals()
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
    def __str__(self):
        return repr(self.value)

class CertExpired(SfaFault):
    def __init__(self, value, extra=None):
        self.value = value
        faultString = "%s cert is expired" % value
        SfaFault.__init__(self, GENICODE.ERROR, faultString, extra)
   
