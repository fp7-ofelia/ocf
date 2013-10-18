# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class GENI_ERROR_CODE:
  """GENI error codes as defined in http://groups.geni.net/geni/wiki/GAPI_AM_API
  
  Based on latest version 2011-11-16

  """
  SERVERBUSY = -32001
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
  MISSINGARGS = 18
  OUTOFRANGE = 19
  CREDENTIAL_INVALID = 20
  CREDENTIAL_EXPIRED = 21
  CREDENTIAL_MISMATCH = 22
  CREDENTIAL_SIGNER_UNTRUSTED = 23
  VLAN_UNAVAILABLE = 24
