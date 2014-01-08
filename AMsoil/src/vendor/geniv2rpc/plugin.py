import amsoil.core.pluginmanager as pm
from g2rpc.genivthree import GENIv2Handler, GENIv2DelegateBase
from g2rpc import exceptions as geni_exceptions

def setup():
    # setup config keys
    config = pm.getService("config")
    config.install("geniv2rpc.cert_root", "deploy/trusted", "Folder which includes trusted clearinghouse certificates for GENI API v2 (in .pem format). If relative path, the root is assumed to be git repo root.")
    config.install("geniv2rpc.rspec_validation", True, "Determines if RSpec shall be validated by the given xs:schemaLocations in the document (may cause downloads of the given schema from the given URL per request).")
    
    # register xmlrpc endpoint
    xmlrpc = pm.getService('xmlrpc')
    geni_handler = GENIv2Handler()
    pm.registerService('geniv2handler', geni_handler)
    pm.registerService('geniv2delegatebase', GENIv3DelegateBase)
    pm.registerService('geniv2exceptions', geni_exceptions)
    xmlrpc.registerXMLRPC('geni2', geni_handler, '/geni2') # name, handlerObj, endpoint
