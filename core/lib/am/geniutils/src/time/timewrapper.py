from types import StringTypes
import dateutil.parser
import datetime
import time

#from openflow.optin_manager.sfa.util.sfalogging import logger

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
        return input
    elif isinstance (input, StringTypes):
        t = dateutil.parser.parse(input)
        if t.utcoffset() is not None:
            t = t.utcoffset() + t.replace(tzinfo=None)
        return t
    elif isinstance (input, (int,float,long)):
        return datetime.datetime.fromtimestamp(input)
    else:
        print "Unexpected type in utcparse [%s]"%type(input)

def datetime_to_string(input):
    return datetime.datetime.strftime(input, DATEFORMAT)

def datetime_to_utc(input):
    return time.gmtime(datetime_to_epoch(input))

def datetime_to_epoch(input):
    return int(time.mktime(input.timetuple()))
