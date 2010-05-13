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

import xmlrpclib
import zlib
from SecureXMLRPCServer import SecureXMLRPCServer

class AggregateManager(object):
    """The public API for a GENI Aggregate Manager.  This class provides the
    XMLRPC interface and invokes a delegate for all the operations.

    """

    def __init__(self, delegate):
        self._delegate = delegate
        
    def GetVersion(self):
        return self._delegate.GetVersion()

    def ListResources(self, credentials, options):
        return self._delegate.ListResources(credentials, options)

    def CreateSliver(self, slice_urn, credentials, rspec):
        return self._delegate.CreateSliver(slice_urn, credentials, rspec)

    def DeleteSliver(self, slice_urn, credentials):
        return self._delegate.DeleteSliver(slice_urn, credentials)

    def SliverStatus(self, slice_urn, credentials):
        return self._delegate.SliverStatus(slice_urn, credentials)

    def RenewSliver(self, slice_urn, credentials, expiration_time):
        return self._delegate.RenewSliver(slice_urn, credentials,
                                          expiration_time)
    def Shutdown(self, slice_urn, credentials):
        return self._delegate.Shutdown(slice_urn, credentials)

class PrintingAggregateManager(object):

    def GetVersion(self):
        print 'GetVersion()'
        return 1

    def ListResources(self, credentials, options):
        compressed = False
        if options and 'geni_compressed' in options:
            compressed  = options['geni_compressed']
        print 'ListResources(compressed=%r)' % (compressed)
        # return an empty rspec
        result = '<rspec/>'
        if compressed:
            result = xmlrpclib.Binary(zlib.compress(result))
        return result

    def CreateSliver(self, slice_urn, credentials, rspec):
        print 'CreateSliver(%r)' % (slice_urn)
        return '<rspec/>'

    def DeleteSliver(self, slice_urn, credentials):
        print 'DeleteSliver(%r)' % (slice_urn)
        return False

    def SliverStatus(self, slice_urn, credentials):
        print 'SliverStatus(%r)' % (slice_urn)
        raise Exception('No such slice.')

    def RenewSliver(self, slice_urn, credentials, expiration_time):
        print 'SliverStatus(%r, %r)' % (slice_urn, expiration_time)
        return False

    def Shutdown(self, slice_urn, credentials):
        print 'Shutdown(%r)' % (slice_urn)
        return False


class AggregateManagerServer(object):
    """An XMLRPC Aggregate Manager Server."""

    def __init__(self, addr, delegate=None, keyfile=None, certfile=None,
                 ca_certs=None):
        self._server = SecureXMLRPCServer(addr, keyfile=keyfile,
                                          certfile=certfile, ca_certs=ca_certs)
        if delegate is None:
            delegate = PrintingAggregateManager()
        self._server.register_instance(AggregateManager(delegate))
        # Set the server on the delegate so it can access the
        # client certificate.
        delegate._server = self._server

    def serve_forever(self):
        self._server.serve_forever()

    def register_instance(self, instance):
        self._server.register_instance(instance)
