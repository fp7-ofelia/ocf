import amsoil.core.pluginmanager as pm
from delegate3 import VTDelegate3

def setup():
    # setup config keys
    config = pm.getService("config")
    delegate = VTDelegate3()
    handler = pm.getService('geniv3handler')
    handler.setDelegate(delegate)
