from flask import Flask, request, request_started, request_finished

import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('flaskrpcs')

from amsoil.core import serviceinterface

from werkzeug import serving
from OpenSSL import SSL, crypto

class ClientCertHTTPRequestHandler(serving.WSGIRequestHandler):
    """Overwrite the werkzeug handler, so we can extract the client cert and put it into the request's environment."""
    def make_environ(self):
        env = super(ClientCertHTTPRequestHandler, self).make_environ()
        if self._client_cert:
            env['CLIENT_RAW_CERT'] = self._client_cert
        return env
        
    def setup(self):
        super(ClientCertHTTPRequestHandler, self).setup()
        self.connection.do_handshake()
        peer_cert = self.connection.get_peer_certificate()
        if peer_cert:
            pem = crypto.dump_certificate(crypto.FILETYPE_PEM, peer_cert)
            self._client_cert = pem
        else:
            self._client_cert = None
        
class FlaskServer(object):
    """
    Encapsules a flask server instance.
    It also exports/defines the rpcservice interface.
    
    When a request comes in the following chain is walked through:
        --http--> nginx webserver --fcgi--> WSGIServer --WSGI--> FlaskApp
    When using the development server:
        werkzeug server --WSGI--> FlaskApp
    """
    
    @serviceinterface
    def __init__(self):
        """Constructur for the server wrapper."""
        self._app = Flask(__name__) # imports the named package, in this case this file

        # Setup debugging for app
        config = pm.getService("config")
        cDebug = config.get("flask.debug")
        if cDebug: # log all actions on the XML-RPC interface
            def log_request(sender, **extra):
                logger.info(">>> REQUEST %s:\n%s" % (request.path, request.data))
            request_started.connect(log_request, self._app)
            def log_response(sender, response, **extra):
                logger.info(">>> RESPONSE %s:\n%s" % (response.status, response.data))
            request_finished.connect(log_response, self._app)

    @property
    def app(self):
        """Returns the flask instance (not part of the service interface, since it is specific to flask)."""
        return self._app

    @serviceinterface
    def runServer(self):
        """Starts up the server. It (will) support different config options via the config plugin."""
        config = pm.getService("config")
        debug = config.get("flask.debug")
        cFCGI = config.get("flask.fcgi")
        host = config.get("flask.bind")
        app_port = config.get("flask.app_port")
        fcgi_port = config.get("flask.fcgi_port")
        must_have_client_cert = config.get("flask.force_client_cert")

        if cFCGI:
            logger.info("registering fcgi server at %s:%i", host, fcgi_port)
            from flup.server.fcgi import WSGIServer
            WSGIServer(self._app, bindAddress=(host, fcgi_port)).run()
        else:
            logger.info("registering app server at %s:%i", host, app_port)
            # do the following line manually, so we can intervene and adjust the ssl context
            # self._app.run(host=host, port=app_port, ssl_context='adhoc', debug=debug, request_handler=ClientCertHTTPRequestHandler)
            
            # the code from flask's `run...`
            # see https://github.com/mitsuhiko/flask/blob/master/flask/app.py
            options = {}
            try:
                # now the code from werkzeug's `run_simple(host, app_port, self._app, **options)`
                # see https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/serving.py
                from werkzeug.debug import DebuggedApplication
                import socket
                application = DebuggedApplication(self._app, True)
                def inner():
                    server = serving.make_server(host, app_port, self._app, False, 1, ClientCertHTTPRequestHandler, False, 'adhoc')
                    # The following line is the reason why I copied all that code!
                    if must_have_client_cert:
                        server.ssl_context.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT, lambda a,b,c,d,e: True)
                    # That's it
                    server.serve_forever()
                address_family = serving.select_ip_version(host, app_port)
                test_socket = socket.socket(address_family, socket.SOCK_STREAM)
                test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                test_socket.bind((host, app_port))
                test_socket.close()
                serving.run_with_reloader(inner, None, 1)
            finally:
                self._app._got_first_request = False
            
