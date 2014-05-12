import amsoil.core.pluginmanager as pm
from delegate import VTDelegate

def setup():
    # setup config keys
    config = pm.getService("config")
    delegate = VTDelegate()
    handler = pm.getService('geniv2handler')
    handler.setDelegate(delegate)
