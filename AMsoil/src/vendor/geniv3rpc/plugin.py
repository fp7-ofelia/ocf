import amsoil.core.pluginmanager as pm
from g3rpc.genivthree import GENIv3Handler, GENIv3DelegateBase
from g3rpc import exceptions as geni_exceptions

def setup():
    # setup config keys
    config = pm.getService("config")
    config.install("geniv3rpc.cert_root", "deploy/trusted", "Folder which includes trusted clearinghouse certificates for GENI API v3 (in .pem format). If relative path, the root is assumed to be git repo root.")
    config.install("geniv3rpc.rspec_validation", True, "Determines if RSpec shall be validated by the given xs:schemaLocations in the document (may cause downloads of the given schema from the given URL per request).")
    
    # register xmlrpc endpoint
    xmlrpc = pm.getService('xmlrpc')
    geni_handler = GENIv3Handler()
    pm.registerService('geniv3handler', geni_handler)
    pm.registerService('geniv3delegatebase', GENIv3DelegateBase)
    pm.registerService('geniv3exceptions', geni_exceptions)
    xmlrpc.registerXMLRPC('geni3', geni_handler, '/RPC2') # name, handlerObj, endpoint
