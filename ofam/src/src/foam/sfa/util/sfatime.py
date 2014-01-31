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
from types import StringTypes
import dateutil.parser
import datetime
import time

#from foam.sfa.util.sfalogging import logger

DATEFORMAT = "%Y-%m-%dT%H:%M:%SZ"

def utcparse(input):
    """ Translate a string into a time using dateutil.parser.parse but make sure it's in UTC time and strip
the timezone, so that it's compatible with normal datetime.datetime objects.

For safety this can also handle inputs that are either timestamps, or datetimes
"""
    # prepare the input for the checks below by
    # casting strings ('1327098335') to ints
    if isinstance(input, StringTypes):
        try:
            input = int(input)
        except ValueError:
            pass

    if isinstance (input, datetime.datetime):
        logger.warn ("argument to utcparse already a datetime - doing nothing")
        return input
    elif isinstance (input, StringTypes):
        t = dateutil.parser.parse(input)
        if t.utcoffset() is not None:
            t = t.utcoffset() + t.replace(tzinfo=None)
        return t
    elif isinstance (input, (int,float,long)):
        return datetime.datetime.fromtimestamp(input)
    else:
        logger.error("Unexpected type in utcparse [%s]"%type(input))

def datetime_to_string(input):
    return datetime.datetime.strftime(input, DATEFORMAT)

def datetime_to_utc(input):
    return time.gmtime(datetime_to_epoch(input))

def datetime_to_epoch(input):
    return int(time.mktime(input.timetuple()))
