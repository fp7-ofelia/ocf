import amsoil.core.pluginmanager as pm
import brm.baseresourcemanager as baseresourcemanager 

def setup():
    pm.registerService('baseresourcemanager',baseresourcemanager)  
