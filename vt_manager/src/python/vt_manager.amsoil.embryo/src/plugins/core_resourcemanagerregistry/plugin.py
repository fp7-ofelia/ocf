import amsoil.core.pluginmanager as pm

from rmr.resourcemanagerregistry import ResourceManagerRegistry
from rmr.resourcemanagerbase import ResourceManagerBase
from rmr.resourcebase import ResourceBase

def setup():
    # Main service
    rmr = ResourceManagerRegistry()
    pm.registerService('resourcemanagerregistry', rmr)
    # Export Interfaces
    pm.registerService('resourcebase', ResourceBase)
    pm.registerService('resourcemanagerbase', ResourceManagerBase)
