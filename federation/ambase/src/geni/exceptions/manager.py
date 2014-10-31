class GENIExceptionManager:
    """
    See http://groups.geni.net/geni/attachment/wiki/GAPI_AM_API_V3/CommonConcepts/geni-error-codes.xml
    """
    SUCCESS = 0
    BADARGS = 1
    ERROR = 2
    FORBIDDEN = 3
    BADVERSION = 4
    SERVERERROR = 5
    TOOBIG = 6
    REFUSED = 7
    TIMEDOUT = 8
    DBERROR = 9
    RPCERROR = 10
    UNAVAILABLE = 11
    SEARCHFAILED = 12
    UNSUPPORTED = 13
    BUSY = 14
    EXPIRED = 15
    INPROGRESS = 16
    ALREADYEXISTS = 17
    VLAN_UNAVAILABLE = 24
    INSUFFICIENT_BANDWIDTH = 25
