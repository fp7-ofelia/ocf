"""
Implements the server functionality (connection,
authentication, etc).

@date: Jun 12, 2013
@author: Laszlo Nagy, msune, CarolinaFernandez
"""

"""SecureXMLRPCServer.py - simple XML RPC server supporting SSL.

Based on this article: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81549

For windows users: http://webcleaner.sourceforge.net/pyOpenSSL-0.6.win32-py2.4.exe

Imported from http://code.activestate.com/recipes/496786-simple-xml-rpc-server-over-https/ 
"""
import SocketServer
import BaseHTTPServer
import SimpleHTTPServer
import SimpleXMLRPCServer
import socket, os

from communications import XmlRpcAPI
from OpenSSL import SSL
from utils.Logger import Logger

from settings import XMLRPC_SERVER_USER, XMLRPC_SERVER_PASSWORD, \
                     XMLRPC_SERVER_LISTEN_HOST,XMLRPC_SERVER_LISTEN_PORT, \
                     XMLRPC_SERVER_KEYFILE,XMLRPC_SERVER_CERTFILE


class SecureXMLRPCServer(BaseHTTPServer.HTTPServer,SimpleXMLRPCServer.SimpleXMLRPCDispatcher):
    def log_request(self, code='-', size='-'): 
        pass

    def __init__(self, server_address, HandlerClass, logRequests=False):
        """Secure XML-RPC server.

        It it very similar to SimpleXMLRPCServer but it uses HTTPS for transporting XML data.
        """
        self.logRequests = logRequests

        SimpleXMLRPCServer.SimpleXMLRPCDispatcher.__init__(self)
        SocketServer.BaseServer.__init__(self, server_address, HandlerClass)
        ctx = SSL.Context(SSL.SSLv23_METHOD)

        ctx.use_privatekey_file (XMLRPC_SERVER_KEYFILE)
        ctx.use_certificate_file(XMLRPC_SERVER_CERTFILE)
        self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
                                                        self.socket_type))
        self.server_bind()
        self.server_activate()

class SecureXMLRpcRequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    """Secure XML-RPC request handler class.

    It it very similar to SimpleXMLRPCRequestHandler but it uses HTTPS for transporting XML data.
    """
    def setup(self):
        self.connection = self.request
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)

    '''
    Request Handler that verifies username and password passed to
    XML RPC server in HTTP URL sent by client.
    '''
    # this is the method we must override
    def parse_request(self):
        if SimpleXMLRPCServer.SimpleXMLRPCRequestHandler.parse_request(self):
            if self.authenticate(self.headers):
                return True
        else:
            self.send_error(401, 'Authentication failed')
            return False

    def authenticate(self, headers):
        """
        Authenticates the headers against the credentials set in the
        configuration file. This method overrides the one with the
        same name in SimpleXMLRPCRequestHandler.

        @return whether authentication was successful or not
		"""
        try:
            from base64 import b64decode
            (basic, _, encoded) = headers.get('Authorization').partition(' ')
            assert basic == 'Basic', 'Only basic authentication supported'
            encodedByteString = encoded.encode()
            decodedBytes = b64decode(encodedByteString)
            decodedString = decodedBytes.decode()
            (username, _, password) = decodedString.partition(':')
            return (username == XMLRPC_SERVER_USER and password == XMLRPC_SERVER_PASSWORD)
        except:
            return False

    def do_POST(self):
        """Handles the HTTPS POST request.

        It was copied out from SimpleXMLRPCServer.py and modified to shutdown the socket cleanly.
        """

        try:
            # get arguments
            data = self.rfile.read(int(self.headers["content-length"]))
            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            response = self.server._marshaled_dispatch(
                    data, getattr(self, '_dispatch', None)
                )
        except: # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            self.send_response(500)
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown() # Modified here!
    
class XmlRpcServer():
	
	logger = Logger.getLogger()

	@staticmethod
	def createInstanceAndEngage(callBackFunction,HandlerClass = SecureXMLRpcRequestHandler,ServerClass = SecureXMLRPCServer):
            server_address = (XMLRPC_SERVER_LISTEN_HOST, XMLRPC_SERVER_LISTEN_PORT) # (address, port)
            server = ServerClass(server_address, HandlerClass)
            server.register_instance(XmlRpcAPI.xmlrpc_wrappers(callBackFunction))
            sa = server.socket.getsockname()
            XmlRpcServer.logger.debug("Serving HTTPS XMLRPC requests on "+str(sa[0])+":"+ str(sa[1]))
            server.serve_forever()

