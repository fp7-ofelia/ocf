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
    config.Config.installConfigItem(config.ConfigItem().setKey("flask.bind").setValue("0.0.0.0").setDesc("IP to bind the Flask RPC to."))
    config.Config.installConfigItem(config.ConfigItem().setKey("flask.port").setValue(9001).setDesc("Port to bind the Flask RPC to."))
    config.Config.installConfigItem(config.ConfigItem().setKey("flask.debug").setValue(True).setDesc("Write logging messages for the Flask RPC server."))
    config.Config.installConfigItem(config.ConfigItem().setKey("flask.wsgi").setValue(True).setDesc("Use WSGI server instead of the development server."))
    # acquire configuration keys
    cBind = config.Config.getConfigItem("flask.bind").getValue()
    cPort = config.Config.getConfigItem("flask.port").getValue()

    # create and register the RPC server
    flaskserver = FlaskServer(cBind, cPort)
    pm.registerService('rpcserver', flaskserver)
    logger.info("registering rpc server at %s:%i", cBind, cPort)

    # create and register the XML-RPC server
    xmlrpc = FlaskXMLRPC(flaskserver)
    pm.registerService('xmlrpc', xmlrpc)

    # TODO create and register the JSON-RPC server