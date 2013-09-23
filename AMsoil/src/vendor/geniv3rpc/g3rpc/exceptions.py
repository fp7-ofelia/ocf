from amsoil.core.exception import CoreException

class GENIv3BaseError(CoreException):
    def __init__(self, code, name, description, comment):
        self.code = code
        self.name = name
        self.description = description
        self.comment = comment

    def __str__(self):
        return "[%s] %s (%s)" % (self.name, self.description, self.comment)


class GENIv3BadArgsError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 1, 'BADARGS', "Bad Arguments", comment) #: Malformed arguments
class GENIv3GeneralError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 2, 'ERROR', "General Error", comment)
class GENIv3ForbiddenError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 3, 'FORBIDDEN', "Operation Forbidden", comment) # eg supplied credentials do not provide sufficient privileges (on given slice)
class GENIv3BadVersionError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 4, 'BADVERSION', "Bad Version", comment) # (eg of RSpec)
class GENIv3ServerError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 5, 'SERVERERROR', "Server Error", comment)
class GENIv3TooBigError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 6, 'TOOBIG', "Too Big", comment) # (eg request RSpec)
class GENIv3RefusedError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 7, 'REFUSED', "Operation Refused", comment)
class GENIv3TimedoutError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 8, 'TIMEDOUT', "Operation Timed Out", comment)
class GENIv3DatabaseError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 9, 'DBERROR', "Database Error", comment)
class GENIv3RPCError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__(10, 'RPCERROR', "RPC Error", comment)
class GENIv3UnavailableError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__(11, 'UNAVAILABLE', "Unavailable", comment) # (eg server in lockdown)
class GENIv3SearchFailedError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__(12, 'SEARCHFAILED', "Search Failed", comment) # (eg for slice)
class GENIv3OperationUnsupportedError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__(13, 'UNSUPPORTED', "Operation Unsupported", comment)
class GENIv3BusyError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__(14, 'BUSY', "Busy, try again later", comment) # (resource, slice)
class GENIv3ExpiredError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__(15, 'EXPIRED', "Expired", comment) # (eg slice)
class GENIv3InProgressError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__(16, 'INPROGRESS', "In Progress", comment)
class GENIv3AlreadyExistsError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__(17, 'ALREADYEXISTS', "Already Exists", comment) # (eg the slice)
class GENIv3VLANUnavailableError(GENIv3BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__(24, 'VLAN_UNAVAILABLE', "VLAN tag(s) requested not available", comment) # (likely stitching failure)