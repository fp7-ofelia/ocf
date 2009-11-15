#!/usr/bin/python

import sys
import os
from optparse import OptionParser
from pprint import pprint
from types import StringTypes

from sfa.util.rspec import Rspec

def create_parser():
    command = sys.argv[0]
    argv = sys.argv[1:]
    usage = "%(command)s [options]" % locals()
    description = """getNodes will open a rspec file and print all key/values, or filter results based on a given key or set of keys."""
    parser = OptionParser(usage=usage,description=description)
    parser.add_option("-i", "--infile", dest="infile", default=None,  help = "input rspec file")
    parser.add_option("-t", "--tag", dest="tag", default=None,  help = "filter rspec for this tag")
    parser.add_option("-a", "--attribute", dest="attribute", default=None,  help = "comma separated list of attributes to display")
    parser.add_option("-r", "--recursive", dest="print_children", default=False,  action="store_true", help = "print the tag's child nodes")

    return parser    


def print_dict(rdict, options, counter=1):
    print_children = options.print_children
    attributes = []
    if options.attribute: 
        attributes = options.attribute.split(',') 
    lists = []
    tab = "    "
    
    if not isinstance(rdict, dict):
        raise "%s not a dict" % rdict 
    for (key, value) in rdict.items():
        if isinstance(value, StringTypes):
            if (attributes and key in attributes) or not attributes:
                print tab * counter + "%s: %s" % (key, value)
        elif isinstance(value, list):
            for listitem in value:
                if isinstance(listitem, dict):
                    lists.append((key, listitem))
        elif isinstance(value, dict):
            lists.append((key, value)) 
    
    if counter == 1 or print_children: 
        for (key, listitem) in lists:
            if isinstance(listitem, dict):
                print tab * (counter - 1) + key
                print_dict(listitem, options, counter+1)
    elif not attributes or (attributes and 'children' in attributes):
        keys = set([key for (key, listitem) in lists])
        if keys: print tab * (counter) + "(children: %s)" % (",".join(keys))    
        

def main():
    parser = create_parser(); 
    (options, args) = parser.parse_args()
    if not options.infile:
        print "Rspec file not specified"
        return 
        
    rspec = Rspec()
    try:
        rspec.parseFile(options.infile)
    except:
        print "Error reading rspec file"

    if options.tag:
        tag_name = options.tag
        rspec_dicts = rspec.getDictsByTagName(tag_name)
        rspec_dict = {tag_name: rspec_dicts}
    else:
        rspec_dict = rspec.toDict()  
  
    print_dict(rspec_dict, options)

    return

if __name__ == '__main__':
    try: main()
    except Exception, e:
        raise
        print e
