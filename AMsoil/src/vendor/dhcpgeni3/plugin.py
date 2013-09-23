import amsoil.core.pluginmanager as pm
from dhcpgenithreedelegate import DHCPGENI3Delegate

def setup():
    # setup config keys
    # config = pm.getService("config")
    
    delegate = DHCPGENI3Delegate()
    handler = pm.getService('geniv3handler')
    handler.setDelegate(delegate)