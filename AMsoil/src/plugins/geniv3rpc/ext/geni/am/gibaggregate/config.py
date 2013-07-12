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


# Configuration information used by multiple modules of the gibaggregate
#    package.

import sys
import logging
import os.path

logger = logging.getLogger('gcf.am2.gib')

# Find the name of the directory in which this script resides
gibDirectory = os.path.dirname(os.path.realpath(__file__))

# Find home directory of user running this aggregate manager
homeDirectory = os.path.expanduser('~')

# Files in the standardScrips subdirectory
standardScriptsDir = gibDirectory + '/standardScripts'
advertRspecFile = 'gib-advert.rspec'  # File containing the advertisement
                                      #     rspec for the aggregate
initAggregate = 'initAggregate.sh'    # shell script that initializes aggregate
deleteSliver = 'deleteSliver.sh'      # shell script that deletes sliver

# Files in the sliceSpecificScripts subdirectory
sliceSpecificScriptsDir = gibDirectory + '/sliceSpecificScripts'
manifestFile = 'gib-manifest.rspec'   # Slice manifest is written to this file
shellScriptFile = 'createSliver.sh'   # Shell script generated to create and
                                      #     configure the sliver

# Figure out the Linux distribution: Red Hat Fedora or Ubuntu
_version = open('/proc/version').read()
if _version.find('Ubuntu') != -1 :
    distro = 'UBUNTU10-STD'
elif _version.find('Red Hat') != -1 :
    distro = 'FEDORA15-STD'
else :
    _exitMsg = 'Running on an unsupported Linux distribution: %s' % _version 
    logger.error(_exitMsg)
    sys.exit(_exitMsg)



rootPwd = 'geniinabox'     # No comment  :-)
