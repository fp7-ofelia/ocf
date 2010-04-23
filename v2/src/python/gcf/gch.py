#!/usr/bin/env python2.6

import sys
import optparse
import geni

class CommandHandler(object):

    def __init__(self):
        self._directory = None

    def parse_opts(self, opts):
        self._directory = opts.directory
        self._infile = opts.infile
        self._outfile = opts.outfile

    def init_handler(self, opts):
        """Handle the init operation."""
        print 'init_handler self = %r' % (self)
        print 'init_handler opts = %r' % (opts)
        self.parse_opts(opts)
        ca = geni.CertificateAuthority()
        ca.newca(self._directory)

    def sign_handler(self, opts):
        """Handle the sign operation. Sign a certificate request."""
        self.parse_opts(opts)
        ca = geni.CertificateAuthority()
        ca.signreq(self._infile, self._outfile, self._directory)

    def runserver_handler(self, opts):
        """Run the clearinghouse server."""
        # XXX Verify that opts.keyfile exists
        # XXX Verify that opts.directory exists
        ch = geni.Clearinghouse()
        # address is a tuple in python socket servers
        addr = (opts.host, opts.port)
        ch.runserver(addr, opts.directory, opts.keyfile, opts.certfile,
                     opts.rootcafile)

    def register_handler(self, opts):
        """Register an aggregate manager."""
        # XXX Implement me
        pass
        

def parse_args(argv):
    parser = optparse.OptionParser()
    parser.add_option("-d", "--directory", default='.',
                      help="directory for config info", metavar="DIR")
    parser.add_option("-o", "--outfile",
                      help="output file name", metavar="FILE")
    parser.add_option("-i", "--infile",
                      help="input file name", metavar="FILE")
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
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    return parser.parse_args()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts, args = parse_args(argv)
    print 'Opts = %r' % (opts)
    print 'Args = %r' % (args)
    handler = '_'.join((args[0], 'handler'))
    ch = CommandHandler()
    return getattr(ch, handler)(opts)

if __name__ == "__main__":
    sys.exit(main())
