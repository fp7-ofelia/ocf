#!/usr/bin/env python2.6

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

import sys
import optparse
import geni

class CommandHandler(object):
    
    # TODO: Implement a register handler to register aggregate managers
    # (persistently) so that a client could ask for the list of
    # aggregate managers.

    def runserver_handler(self, opts):
        """Run the clearinghouse server."""
        # XXX Verify that opts.keyfile exists
        # XXX Verify that opts.directory exists
        ch = geni.Clearinghouse()
        # address is a tuple in python socket servers
        addr = (opts.host, opts.port)
        ch.runserver(addr, opts.keyfile, opts.certfile, opts.rootcafile)

def parse_args(argv):
    parser = optparse.OptionParser()
    parser.add_option("-k", "--keyfile",
                      help="key file name", metavar="FILE")
    parser.add_option("-c", "--certfile",
                      help="certificate file name", metavar="FILE")
    parser.add_option("-r", "--rootcafile",
                      help="root ca certificate file name", metavar="FILE")
    # Could try to determine the real IP Address instead of the loopback
    # using socket.gethostbyname(socket.gethostname())
    parser.add_option("-H", "--host", default='127.0.0.1',
                      help="server ip", metavar="HOST")
    parser.add_option("-p", "--port", type=int, default=8000,
                      help="server port", metavar="PORT")
    parser.add_option("--debug", action="store_true", default=False,
                       help="enable debugging output")
    return parser.parse_args()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts, args = parse_args(argv)
    if not args:
        args = ('runserver',)
    handler = '_'.join((args[0], 'handler'))
    ch = CommandHandler()
    if hasattr(ch, handler):
        return getattr(ch, handler)(opts)
    else:
        print >> sys.stderr, 'Unknown command ', args[0]

if __name__ == "__main__":
    sys.exit(main())
