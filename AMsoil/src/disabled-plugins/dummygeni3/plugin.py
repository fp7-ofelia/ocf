import amsoil.core.pluginmanager as pm
from dummydelegate import DummyDelegate

def setup():
    # setup config keys
    # config = pm.getService("config")
    
    delegate = DummyDelegate()
    handler = pm.getService('geniv3handler')
    handler.setDelegate(delegate)
