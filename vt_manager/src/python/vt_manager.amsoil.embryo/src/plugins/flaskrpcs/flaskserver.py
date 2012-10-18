from flask import Flask, request, request_started, request_finished

import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('flaskrpcs')

from amsoil.core import serviceinterface

class FlaskServer():
    """
    Encapsules a flask server instance.
    It also exports/defines the rpcservice interface.
    """
    
    @serviceinterface
    def __init__(self, host, port):
        """Constructur for the server wrapper."""
        self._app = Flask(__name__) # imports the named package, in this case this file
        self._host = host
        self._port = port

        # Setup debugging for app
        config = pm.getService("config")
        cDebug = config.Config.getConfigItem("flask.debug").getValue()
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
        cWSGI = config.Config.getConfigItem("flask.wsgi").getValue()
        if cWSGI:
            from flup.server.fcgi import WSGIServer
            WSGIServer(self._app, bindAddress=(self._host, self._port)).run()
        else:
            self._app.run(host=self._host, port=self._port, ssl_context='adhoc')        