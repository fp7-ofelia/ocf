# PyCURL based transports for xmlrpclib
#
# Modified from the example by Alexandr Kanevskiy
#
# Copyright (C) 2010 Jad Naous <jnaous () gm ail.com>
# Copyright (C) 2008 Alexandr D. Kanevskiy <kad () bifh.org>
#
# Based on pycurl's example by Kjetil Jacobsen <kjetilja at gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
#
# $Id$
from pprint import pprint

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import xmlrpclib

class PyCURLTransport(xmlrpclib.Transport):
    """Handles a cURL HTTP transaction to an XML-RPC server."""

    def __init__(self, username = None, password = None, timeout = 300):
        import pycurl
        
        xmlrpclib.Transport.__init__(self)

        self.verbose = 0
        self._proto = "http"

        self._curl = pycurl.Curl()

        # Suppress signals
        self._curl.setopt(pycurl.NOSIGNAL, 1)

        # Follow redirects
        self._curl.setopt(pycurl.FOLLOWLOCATION, 1)

        # Set timeouts
        if timeout:
            self._curl.setopt(pycurl.CONNECTTIMEOUT, timeout)
            self._curl.setopt(pycurl.TIMEOUT, timeout)

        # XML-RPC calls are POST (text/xml)
        self._curl.setopt(pycurl.POST, 1)
        self._curl.setopt(pycurl.HTTPHEADER, [ "Content-Type: text/xml" ])

        # Set auth info if defined
        if username != None and password != None:
            self._curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
            self._curl.setopt(
                pycurl.USERPWD,
                ("%s:%s" % (username, password)).encode('ascii'))

    def _check_return(self, host, handler, httpcode, buf):
        """Checks return code for various errors"""
        pass

    def request(self, host, handler, request_body, verbose = 0):
        """Performs actual request"""
        
        import pycurl

        buf = StringIO()
        self._curl.setopt(
            pycurl.URL, 
            ("%s://%s%s" % (self._proto, host, handler)).encode('ascii'))
        self._curl.setopt(pycurl.POSTFIELDS, request_body)
        self._curl.setopt(pycurl.WRITEFUNCTION, buf.write)
        self._curl.setopt(pycurl.VERBOSE, verbose)
        self.verbose = verbose
        try:
            self._curl.perform()
            httpcode = self._curl.getinfo(pycurl.HTTP_CODE)
        except pycurl.error, err:
            raise xmlrpclib.ProtocolError( 
                    host + handler, 
                    err[0], 
                    err[1], 
                    None)

        self._check_return(host, handler, httpcode, buf)

        if httpcode != 200:
            raise xmlrpclib.ProtocolError( 
                    host + handler, 
                    httpcode, 
                    buf.getvalue(), 
                    None)

        buf.seek(0)
        return self.parse_response(buf)


class PyCURLSafeTransport(PyCURLTransport):
    """Handles a cURL HTTP transaction to an XML-RPC server
    and also can validate certs."""
    def __init__(self, username = None, password = None,
                 timeout = 300, ca_cert_path = None, ca_cert_file = None):

        PyCURLTransport.__init__(self, username, password, timeout)

        self._proto = "https"
        
        self.set_ssl_verify(ca_cert_path, ca_cert_file)

    def _check_return(self, host, handler, httpcode, buf):
        """Check for SSL certs validity"""
        
        if httpcode == 60:
            raise xmlrpclib.ProtocolError( 
                host + handler, 
                httpcode, 
                "SSL certificate validation failed", 
                None)
            
    def set_ssl_verify(self, ca_cert_path=None, ca_cert_file=None):
        '''Enable/disable SSL verification'''
        
        import pycurl
        
        self._curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        self._curl.setopt(pycurl.SSL_VERIFYHOST, 0)
        # Setup certificates
        if ca_cert_file or ca_cert_path:
            self._curl.setopt(pycurl.CAPATH, ca_cert_file or ca_cert_path)
            self._curl.setopt(pycurl.SSL_VERIFYPEER, 1)
            self._curl.setopt(pycurl.SSL_VERIFYHOST, 2)
            
class TestClientTransport(xmlrpclib.Transport):
    """Handles connections to XML-RPC server through Django test client"""
    
    def __init__(self, *args, **kwargs):
        from django.test.client import Client
        self.client = Client()

    def request(self, host, handler, request_body, verbose=0):
        self.verbose = verbose
        response = self.client.post(handler,
                                    request_body,
                                    content_type="text/xml")
        res = StringIO(response.content)
        res.seek(0)
        return self.parse_response(res)
    