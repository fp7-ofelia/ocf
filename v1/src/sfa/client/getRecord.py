#!/usr/bin/python

"""
Filters/Prints record objects


faiyaza at cs dot princeton dot edu
Copyright (c) 2009 Board of Trustees, Princeton University

$Id: getRecord.py 14252 2009-07-03 14:40:59Z thierry $
$HeadURL$
"""

import sys
import os
from optparse import OptionParser
from pprint import pprint
from xml.parsers.expat import ExpatError

from sfa.util.rspec import RecordSpec


def create_parser():
    command = sys.argv[0]
    argv = sys.argv[1:]
    usage = "%(command)s [options]" % locals()
    description = """getRecord will parse a supplied (via stdin) record and print all values or key/values, and filter results based on a given key or set of keys."""
    parser = OptionParser(usage=usage,description=description)
    parser.add_option("-d", "--debug", dest="DEBUG", action="store_true",
        default=False,  help = "record file path")
    parser.add_option("-k", "--key", dest="withkey", action="store_true",
        default=False,  help = "print SSH keys and certificates")
    parser.add_option("-p", "--plinfo", dest="plinfo", action="store_true",
        default=False,  help = "print PlanetLab specific internal fields")
   
    return parser    


def printRec(record, filters, options):
    line = ""
    if len(filters):
        for filter in filters:
            if options.DEBUG:  print "Filtering on %s" %filter
            line += "%s: %s\n" % (filter, 
                printVal(record.dict["record"].get(filter, None)))
        print line
    else:
        # print the wole thing
        for (key, value) in record.dict["record"].iteritems():
            if (not options.withkey and key in ('gid', 'keys')) or\
                (not options.plinfo and key == 'pl_info'):
                continue
            line += "%s: %s\n" % (key, printVal(value))
        print line


# fix the iteratable values
def printVal(value):
    line = ""
    if type(value) in (tuple, list):
        for i in value:
            line += "%s " % i
    elif value != None:
        line += value
    return line.rstrip("\n")


def main():
    parser = create_parser(); 
    (options, args) = parser.parse_args()

    stdin = sys.stdin.read()
    
    record = RecordSpec(xml = stdin)
    
    if not record.dict.has_key("record"):
        raise "RecordError", "Input record does not have 'record' tag."

    if options.DEBUG: 
        record.pprint()
        print "#####################################################"

    printRec(record, args, options)

if __name__ == '__main__':
    try: main()
    except ExpatError, e:
        print "RecordError.  Is your record valid XML?"
        print e
    except Exception, e:
        print e
