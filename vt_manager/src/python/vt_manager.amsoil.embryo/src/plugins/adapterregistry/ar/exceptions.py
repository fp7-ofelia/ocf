from amsoil.core.exception import CoreException

class AlreadyRegisteredError(CoreException):
    pass

class NotRegisteredError(CoreException):
    pass
