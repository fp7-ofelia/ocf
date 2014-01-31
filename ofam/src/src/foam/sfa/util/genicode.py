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

from foam.sfa.util.enumeration import Enum

GENICODE = Enum(
    SUCCESS=0,
    BADARGS=1,
    ERROR=2,
    FORBIDDEN=3,
    BADVERSION=4,
    SERVERERROR=5,
    TOOBIG=6,
    REFUSED=7,
    TIMEDOUT=8,
    DBERROR=9,
    RPCERROR=10,
    UNAVAILABLE=11,
    SEARCHFAILED=12,
    UNSUPPORTED=13,
    BUSY=14,
    EXPIRED=15,
    INPORGRESS=16,
    ALREADYEXISTS=17       
)   
