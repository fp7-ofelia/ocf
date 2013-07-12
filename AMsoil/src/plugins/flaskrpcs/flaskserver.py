from flask import Flask, request, request_started, request_finished

import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('flaskrpcs')

from amsoil.core import serviceinterface

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

        if cFCGI:
            logger.info("registering fcgi server at %s:%i", host, fcgi_port)
            from flup.server.fcgi import WSGIServer
            WSGIServer(self._app, bindAddress=(host, fcgi_port)).run()
        else:
            logger.info("registering app server at %s:%i", host, app_port)
            self._app.run(host=host, port=app_port, ssl_context='adhoc', debug=debug)