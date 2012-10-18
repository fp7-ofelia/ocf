import amsoil.core.pluginmanager as pm

from ipresource import IPResource
from dhcpr.exceptions import ResourceReservationInterruptedError

ResourceManagerBase = pm.getService('resourcemanagerbase')

class IPResourceManager(ResourceManagerBase):
    def __init__(self):
        super(IPResourceManager, self).__init__([IPResource])
        self._database = []

    def list(self, **options):
        """Returns all allocated resources."""
        return self._database[:]

    def find(self, uuid, **options):
        for ipRes in self._database:
            if ipRes.uuid == uuid:
                return ipRes
        return None

    def findBySliceURN(self, sliceURN): # GENI specific method
        # no slice URNs here for simplicity
        return self._database[:]

    # Reservation methods
    def temporallyReserve(self, **options):
        pass 

    def reserve(self, uuid, **options):
        ip=options['ip']
        # check if the IP is taken already
        for ipRes in self._database:
            if (ipRes.ip == ip):
                raise ResourceReservationInterruptedError("The IP %s has already been reserved." % (ip,))
        # create the resource
        resource = IPResource(ip)
        resource.start()
        # and put it into the database
        self._database.append(resource)
        return resource

    def release(self, uuid, **options):
        for ipRes in self._database:
            if (ipRes.uuid == uuid):
                ipRes.stop()
                self._database.remove(ipRes)
