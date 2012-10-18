import amsoil.core.pluginmanager as pm

from crpc.configrpc import ConfigRPC

def setup():
    # setup config keys
    # config = pm.getService("config")
    # config.Config.installConfigItem(config.ConfigItem().setKey("geniv2rpc.cert_root").setValue("~/.gcf/trusted_roots").setDesc("Folder which includes trusted clearinghouse certificates for GENI API v2 (in .pem format)"))
    xmlrpc = pm.getService('xmlrpc')
    xmlrpc.registerXMLRPC('configrpc', ConfigRPC(), '/amconfig') # handlerObj, endpoint