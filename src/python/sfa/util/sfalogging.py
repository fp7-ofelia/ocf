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

import logging
import os

#SFA access log initialization
TMPDIR = os.getenv("TMPDIR", "/tmp")
SFA_HTTPD_ACCESS_LOGFILE = TMPDIR + "/" + 'sfa_httpd_access.log'
SFA_ACCESS_LOGFILE='/var/log/sfa_access.log'
logger=logging.getLogger('sfa')
logger.setLevel(logging.INFO)

try:
    logfile=logging.FileHandler(SFA_ACCESS_LOGFILE)
except IOError:
    # This is usually a permissions error becaue the file is
    # owned by root, but httpd is trying to access it.
    try:
        logfile = logging.FileHandler(SFA_HTTPD_ACCESS_LOGFILE)
    except IOError as e:
        if e.errno != 13:
            raise
        
        logfile = None
        i = 1
        while i < 10 and not logfile:
            tmp_fname = SFA_HTTPD_ACCESS_LOGFILE + ".%s" % i
            try:
                logfile = logging.FileHandler(tmp_fname)
                break
            except IOError as e:
                if e.errno != 13:
                    raise
            i = i + 1
        if i < 10:
            SFA_HTTPD_ACCESS_LOGFILE = tmp_fname
    
formatter = logging.Formatter("%(asctime)s - %(message)s")
logfile.setFormatter(formatter)
logger.addHandler(logfile)
def get_sfa_logger():
    return logger
