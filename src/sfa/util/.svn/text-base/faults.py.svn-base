#
# GeniAPI XML-RPC faults
#
#

### $Id$
### $URL$

import xmlrpclib

class GeniFault(xmlrpclib.Fault):
    def __init__(self, faultCode, faultString, extra = None):
        if extra:
            faultString += ": " + extra
        xmlrpclib.Fault.__init__(self, faultCode, faultString)

class GeniInvalidAPIMethod(GeniFault):
    def __init__(self, method, interface = None, extra = None):
        faultString = "Invalid method " + method
        if interface:
            faultString += " for interface " + interface
        GeniFault.__init__(self, 100, faultString, extra)

class GeniInvalidArgumentCount(GeniFault):
    def __init__(self, got, min, max = min, extra = None):
        if min != max:
            expected = "%d-%d" % (min, max)
        else:
            expected = "%d" % min
        faultString = "Expected %s arguments, got %d" % \
                      (expected, got)
        GeniFault.__init__(self, 101, faultString, extra)

class GeniInvalidArgument(GeniFault):
    def __init__(self, extra = None, name = None):
        if name is not None:
            faultString = "Invalid %s value" % name
        else:
            faultString = "Invalid argument"
        GeniFault.__init__(self, 102, faultString, extra)

class GeniAuthenticationFailure(GeniFault):
    def __init__(self, extra = None):
        faultString = "Failed to authenticate call"
        GeniFault.__init__(self, 103, faultString, extra)

class GeniDBError(GeniFault):
    def __init__(self, extra = None):
        faultString = "Database error"
        GeniFault.__init__(self, 106, faultString, extra)

class GeniPermissionDenied(GeniFault):
    def __init__(self, extra = None):
        faultString = "Permission denied"
        GeniFault.__init__(self, 108, faultString, extra)

class GeniNotImplemented(GeniFault):
    def __init__(self, extra = None):
        faultString = "Not fully implemented"
        GeniFault.__init__(self, 109, faultString, extra)

class GeniAPIError(GeniFault):
    def __init__(self, extra = None):
        faultString = "Internal API error"
        GeniFault.__init__(self, 111, faultString, extra)

class MalformedHrnException(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Malformed HRN: %(value)s" % locals()
        GeniFault.__init__(self, 102, faultString, extra)
    def __str__(self):
        return repr(self.value)

class TreeException(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Tree Exception: %(value)s, " % locals()
        GeniFault.__init__(self, 111, faultString, extra)
    def __str__(self):
        return repr(self.value)

class NonexistingRecord(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Non exsiting record %(value)s, " % locals()
        GeniFault.__init__(self, 111, faultString, extra)
    def __str__(self):
        return repr(self.value)

class ExistingRecord(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Existing record: %(value)s, " % locals()
        GeniFault.__init__(self, 111, faultString, extra)
    def __str__(self):
        return repr(self.value)
        
class NonexistingCredType(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Non existing record: %(value)s, " % locals()
        GeniFault.__init__(self, 111, faultString, extra)
    def __str__(self):
        return repr(self.value)

class NonexistingFile(GeniFault):
    def __init__(self, value):
        self.value = value
        faultString = "Non existing file: %(value)s, " % locals()
        GeniFault.__init__(self, 111, faultString, extra)
    def __str__(self):
        return repr(self.value)

class InvalidRPCParams(GeniFault):
    def __init__(self, value):
        self.value = value
        faultString = "Invalid RPC Params: %(value)s, " % locals()
        GeniFault.__init__(self, 102, faultString, extra)
    def __str__(self):
        return repr(self.value)

# SMBAKER exceptions follow

class ConnectionKeyGIDMismatch(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Connection Key GID mismatch: %(value)s" % locals()
        GeniFault.__init__(self, 102, faultString, extra) 
    def __str__(self):
        return repr(self.value)

class MissingCallerGID(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Missing Caller GID: %(value)s" % locals()
        GeniFault.__init__(self, 102, faultString, extra) 
    def __str__(self):
        return repr(self.value)

class RecordNotFound(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Record not found: %(value)s" % locals()
        GeniFault.__init__(self, 102, faultString, extra)
    #def __str__(self):
    #    return repr(self.value)

class UnknownGeniType(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Unknown Geni Type: %(value)s" % locals()
        GeniFault.__init__(self, 102, faultString, extra)
    def __str__(self):
        return repr(self.value)

class MissingAuthority(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Missing authority: %(value)s" % locals()
        GeniFault.__init__(self, 102, faultString, extra)
    def __str__(self):
        return repr(self.value)

class PlanetLabRecordDoesNotExist(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "PlanetLab record does not exist : %(value)s" % locals()
        GeniFault.__init__(self, 102, faultString, extra)
    def __str__(self):
        return repr(self.value)

class PermissionError(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Permission error: %(value)s" % locals()
        GeniFault.__init__(self, 108, faultString, extra)
    def __str__(self):
        return repr(self.value)

class InsufficientRights(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Insufficient rights: %(value)s" % locals()
        GeniFault.__init__(self, 108, faultString, extra)
    def __str__(self):
        return repr(self.value)

class MissingDelegateBit(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Missing delegate bit: %(value)s" % locals()
        GeniFault.__init__(self, 108, faultString, extra)
    def __str__(self):
        return repr(self.value)

class ChildRightsNotSubsetOfParent(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Child rights not subset of parent: %(value)s" % locals()
        GeniFault.__init__(self, 103, faultString, extra)
    def __str__(self):
        return repr(self.value)

class CertMissingParent(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Cert missing parent: %(value)s" % locals()
        GeniFault.__init__(self, 103, faultString, extra)
    def __str__(self):
        return repr(self.value)

class CertNotSignedByParent(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Cert not signed by parent: %(value)s" % locals()
        GeniFault.__init__(self, 103, faultString, extra)
    def __str__(self):
        return repr(self.value)

class GidInvalidParentHrn(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "GID invalid parent hrn: %(value)s" % locals()
        GeniFault.__init__(self, 102, faultString, extra)
    def __str__(self):
        return repr(self.value)

class SliverDoesNotExist(GeniFault):
    def __init__(self, value, extra = None):
        self.value = value
        faultString = "Sliver does not exist : %(value)s" % locals()
        GeniFault.__init__(self, 102, faultString, extra)
    def __str__(self):
        return repr(self.value)

