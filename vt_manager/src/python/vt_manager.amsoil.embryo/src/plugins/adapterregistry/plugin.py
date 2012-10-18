import amsoil.core.pluginmanager as pm

from ar.adapterregistry import AdapterRegistry
from ar.adapterbase import AdapterBase

def setup():
    ar = AdapterRegistry()
    pm.registerService('adapterbase', AdapterBase)
    pm.registerService('adapterregistry', ar)
