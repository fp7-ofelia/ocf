import amsoil.core.pluginmanager as pm

ResourceBase = pm.getService('resourcebase')

class IPResource(ResourceBase):
    def __init__(self, ip=None):
        self.uuid = self.createUUID()
        self._ip = ip

    @property
    def ip(self):
        return self._ip

    def start(self):
        # actual implementation omited for simplicity
        pass

    def stop(self):
        # actual implementation omited for simplicity
        pass
    
    def getOperationalState(self):
        # actual implementation omited for simplicity
        return 'ready'
    
    def renew(self, time): # renew exparation time
        # actual implementation omited for simplicity
        # let's say we were successful, so we do not throw an exception
        pass
