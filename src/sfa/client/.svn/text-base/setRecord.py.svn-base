#!/usr/bin/python

"""
Updates record objects


faiyaza at cs dot princeton dot edu
Copyright (c) 2009 Board of Trustees, Princeton University

$Id$
$HeadURL$
"""

import sys
import os
from optparse import OptionParser
from pprint import pprint

from sfa.util.rspec import RecordSpec


def create_parser():
    command = sys.argv[0]
    argv = sys.argv[1:]
    usage = "%(command)s [options]" % locals()
    description = """setRecord will edit a record (from stdin), modify its contents, then print the new record to stdout"""
    parser = OptionParser(usage=usage,description=description)
    parser.add_option("-d", "--debug", dest="DEBUG", action="store_true",
        default=False,  help = "print debug info")
   
    return parser    


def editDict(args, recordDict, options):
    """
    Takes the arg list, seperates into tag/value, creates a dict, then munges args.
    """
    # find out if its iterable.
    for vect in args:
        if vect.count("+="):
            # append value
            modDict({vect.split("+=")[0]: returnVal(vect.split("+=")[1])},
                         recordDict, options) 
 
        elif vect.count("="):
            # reassign value
            replaceDict({vect.split("=")[0]: returnVal("=".join(vect.split("=")[1:]))},
                         recordDict, options) 
        else:
            if vect in recordDict:
                del recordDict[vect]
            else:
                raise TypeError, "Argument error: Records are updated with \n" \
                            "key=val1,val2,valN or\n" \
                            "key+=val1,val2,valN \n%s Unknown key/val" % vect


def replaceDict(newval, recordDict, options):
    """
    Replaces field in dict
    """
    # Check type of old field matches type of new field
    for (key, val) in newval.iteritems():
        recordDict[key] = val

def modDict(newval, recordDict, options):
    """
    Checks type of existing field, addends new field
    """
    for (key, val) in newval.iteritems():
        if (type(recordDict[key]) == list):
            if (type(val) == list):
                recordDict[key] = recordDict[key] + val
            else:
                recordDict[key].append(val)
        elif type(val) == list:
            val.append(recordDict[key])
            recordDict[key] = val
        else:
            recordDict[key] = [recordDict[key], val]


def returnVal(arg):
    """
    if given input has ",", then its assumed to be a list.
    """
    if arg.count(","):
        return list(arg.split(","))
    else:
        return arg

def main():
    parser = create_parser(); 
    (options, args) = parser.parse_args()

    record = RecordSpec(xml = sys.stdin.read())

    if args:
        editDict(args, record.dict["record"], options)
    if options.DEBUG:
        print "New Record:\n%s" % record.dict
        record.pprint()

    record.parseDict(record.dict)
    s = record.toxml()
    sys.stdout.write(s)

if __name__ == '__main__':
    try: main()
    except Exception, e:
        print e
