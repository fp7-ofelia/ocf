"""A simple XML RPC server supporting SSL.

Based on this article:
   http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81549

"""

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SocketServer import TCPServer
import socket, os
import ssl

class SecureXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):
    """A request handler that grabs the socket peer's certificate and
    makes it available while the request is handled.

    This implementation can only be used in a single-threaded, one
    request at a time model. The peer certificate is stashed on the
    XML RPC server at the start of a call and removed at the end of a
    call. This is the only way I could find to access this
    information.
    """

    def setup(self):
        SimpleXMLRPCRequestHandler.setup(self)
        self.server.peercert = self.request.getpeercert()

    def finish(self):
        # XXX do we want to delete the peercert attribute?
        # If so, use:        del self.server.peercert
        self.server.peercert = None
        SimpleXMLRPCRequestHandler.finish(self)
        

class SecureXMLRPCServer(SimpleXMLRPCServer):
    """An extension to SimpleXMLRPCServer that adds SLL support."""

    def __init__(self, addr, requestHandler=SecureXMLRPCRequestHandler,
                 logRequests=False, allow_none=False, encoding=None,
                 bind_and_activate=True, keyfile=None, certfile=None,
                 ca_certs=None):
        SimpleXMLRPCServer.__init__(self, addr, requestHandler, logRequests,
                                    allow_none, encoding, False)
        self.socket = ssl.wrap_socket(self.socket,
                                      keyfile=keyfile,
                                      certfile=certfile,
                                      server_side=True,
                                      cert_reqs=ssl.CERT_REQUIRED,
                                      ssl_version=ssl.PROTOCOL_SSLv23,
                                      ca_certs=ca_certs)
        if bind_and_activate:
            self.server_bind()
            self.server_activate()
