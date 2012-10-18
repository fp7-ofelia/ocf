from amsoil.core.exception import CoreException

class ResourceReservationInterruptedError(CoreException):
    def __init__(self, reason):
        self._reason = reason
    def __str__(self):
        return repr("Resource reservation was interrupted du to \"%s\". Other resources might have been reserved. Please check by listing all resources." % (self._reason,))
