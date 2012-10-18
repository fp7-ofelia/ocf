import amsoil.core.pluginmanager as pm
from g2rpc.genivtworpc import GENIv2RPC
from g2rpc.genitwoadapterbase import GENI2AdapterBase

def setup():
    # setup config keys
    config = pm.getService("config")
    config.Config.installConfigItem(config.ConfigItem().setKey("geniv2rpc.cert_root").setValue("~/.gcf/trusted_roots").setDesc("Folder which includes trusted clearinghouse certificates for GENI API v2 (in .pem format)"))
    # register xmlrpc endpoint
    xmlrpc = pm.getService('xmlrpc')
    xmlrpc.registerXMLRPC('geni2', GENIv2RPC(), '/RPC2') # name, handlerObj, endpoint
    # and adapter base
    pm.registerService('geni2adapterbase', GENI2AdapterBase)