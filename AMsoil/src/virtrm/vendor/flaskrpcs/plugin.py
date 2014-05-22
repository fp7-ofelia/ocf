"""
Please see the documentation in FlaskXMLRPC.
"""
import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('flaskrpcs')

from flaskxmlrpc import FlaskXMLRPC
from flaskserver import FlaskServer

def setup():
    config = pm.getService("config")
    # create default configurations (if they are not already in the database)
    config.install("flask.bind", "0.0.0.0", "IP to bind the Flask RPC to.")
    config.install("flask.fcgi_port", 9001, "Port to bind the Flask RPC to (FCGI server).")
    config.install("flask.app_port", 8003, "Port to bind the Flask RPC to (standalone server).")
    config.set("flask.app_port", 8023)
    config.install("flask.debug", True, "Write logging messages for the Flask RPC server.")
    config.install("flask.fcgi", False, "Use FCGI server instead of the development server.")
    config.install("flask.force_client_cert", True, "Only applies if flask.debug is set: Determines if the client _must_ present a certificate. No validation is performed.")
    

    # create and register the RPC server
    flaskserver = FlaskServer()
    pm.registerService('rpcserver', flaskserver)

    # create and register the XML-RPC server
    xmlrpc = FlaskXMLRPC(flaskserver)
    pm.registerService('xmlrpc', xmlrpc)

    # TODO create and register the JSON-RPC server
