#!/usr/bin/python

#----------------------------------------------------------------------
# Copyright (c) 2012 Raytheon BBN Technologies
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
"""
Error codes
"""

## Pulled from: http://groups.geni.net/geni/attachment/wiki/GAPI_AM_API_V3/CommonConcepts/geni-error-codes.xml
err_codes = {}
err_codes[ 0 ] = { 'label': 'SUCCESS', 'description': "Success" }
err_codes[ 1 ] = { 'label': 'BADARGS', 'description': "Bad Arguments: malformed arguments" }
err_codes[ 2 ] = { 'label': 'ERROR', 'description': "Error (other)" }
err_codes[ 3 ] = { 'label': 'FORBIDDEN', 'description': "Operation Forbidden: eg supplied credentials do not provide sufficient privileges (on given slice)" }
err_codes[ 4 ] = { 'label': 'BADVERSION', 'description': "Bad Version (eg of RSpec)" }
err_codes[ 5 ] = { 'label': 'SERVERERROR', 'description': "Server Error" }
err_codes[ 6 ] = { 'label': 'TOOBIG', 'description': "Too Big (eg request RSpec)" }
err_codes[ 7 ] = { 'label': 'REFUSED', 'description': "Operation Refused" }
err_codes[ 8 ] = { 'label': 'TIMEDOUT', 'description': "Operation Timed Out" }
err_codes[ 9 ] = { 'label': 'DBERROR', 'description': "Database Error" }
err_codes[ 10 ] = { 'label': 'RPCERROR', 'description': "RPC Error" }
err_codes[ 11 ] = { 'label': 'UNAVAILABLE', 'description': "Unavailable (eg server in lockdown)" }
err_codes[ 12 ] = { 'label': 'SEARCHFAILED', 'description': "Search Failed (eg for slice)" }
err_codes[ 13 ] = { 'label': 'UNSUPPORTED', 'description': "Operation Unsupported" }
err_codes[ 14 ] = { 'label': 'BUSY', 'description': "Busy (resource, slice, or server); try again later" }
err_codes[ 15 ] = { 'label': 'EXPIRED', 'description': "Expired (eg slice)" }
err_codes[ 16 ] = { 'label': 'INPROGRESS', 'description': "In Progress" }
err_codes[ 17 ] = { 'label': 'ALREADYEXISTS', 'description': "Already Exists (eg the slice}" }
err_codes[ 18 ] = { 'label': 'MISSINGARGS', 'description': "Required argument(s) missing" }
err_codes[ 19 ] = { 'label': 'OUTOFRANGE', 'description': "Requested expiration time or other argument not valid" }
err_codes[ 20 ] = { 'label': 'CREDENTIAL_INVALID', 'description': "Not authorized: Supplied credential is invalid" }
err_codes[ 21 ] = { 'label': 'CREDENTIAL_EXPIRED', 'description': "Not authorized: Supplied credential expired" }
err_codes[ 22 ] = { 'label': 'CREDENTIAL_MISMATCH', 'description': "Not authorized: Supplied credential does not match the supplied client certificate or does not match the given slice URN" }
err_codes[ 23 ] = { 'label': 'CREDENTIAL_SIGNER_UNTRUSTED', 'description': "Not authorized: Supplied credential not signed by trusted authority" } 
err_codes[ 24 ] = { 'label': 'VLAN_UNAVAILABLE', 'description': "VLAN tag(s) requested not available (likely stitching failure)" } 
