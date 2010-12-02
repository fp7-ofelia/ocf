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

class SafeTransportWithCert(xmlrpclib.SafeTransport):
    '''Sample client for talking XMLRPC over SSL supplying
    a client X509 identity certificate.'''
    def __init__(self, use_datetime=0, keyfile=None, certfile=None,
                 timeout=None):
        xmlrpclib.SafeTransport.__init__(self, use_datetime)
        self.__x509 = dict()
        if keyfile:
            self.__x509['key_file'] = keyfile
        if certfile:
            self.__x509['cert_file'] = certfile
        self._timeout = timeout

    def make_connection(self, host):
        host_tuple = (host, self.__x509)
        conn = xmlrpclib.SafeTransport.make_connection(self, host_tuple)
        if self._timeout:
            conn._conn.timeout = self._timeout
        return conn
    

    
def make_client(url, keyfile, certfile, verbose=False, timeout=None):
    """Create an SSL connection to an XML RPC server.
    Returns the XML RPC server proxy.
    """
    cert_transport = SafeTransportWithCert(keyfile=keyfile, certfile=certfile,
                                           timeout=timeout)
    return xmlrpclib.ServerProxy(url, transport=cert_transport,
                                 verbose=verbose)
