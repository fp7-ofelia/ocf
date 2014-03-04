import amsoil.core.pluginmanager as pm

from crpc.configrpc import ConfigRPC

def setup():
    # setup config keys
    xmlrpc = pm.getService('xmlrpc')
    xmlrpc.registerXMLRPC('configrpc', ConfigRPC(), '/amconfig') # handlerObj, endpoint