#----------------------------------------------------------------------
# Copyright (c) 2010 Raytheon BBN Technologies
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

import ConfigParser
import os

def read_config(path=None):
    """Read the config file into a dictionary where each section
    of the config is its own sub-dictionary
    """
    confparser = ConfigParser.RawConfigParser()
    paths = ['gcf_config', os.path.expanduser('~/.gcf/gcf_config'),
             '/etc/gcf-servers/gcf_config']
    if path:
        paths.insert(0, path)

    foundFile = None
    for file in paths:
        foundFile = confparser.read(file)
        if foundFile:
            break

    if not foundFile:
        import sys
        sys.exit("Config file could not be found or was not properly formatted (I searched in paths: %s)" % paths)

    config = {}

    for section in confparser.sections():
        config[section] = {}
        for (key,val) in confparser.items(section):
            config[section][key] = val

    return config
