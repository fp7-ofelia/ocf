from amsoil.core.exception import CoreException

class AlreadyRegisteredError(CoreException):
    '''Already registered exception'''
    pass

class InvalidSupportedResourceTypeError(CoreException):
    '''Invalid type. Must be Resource instance'''
    pass

class NotRegisteredError(CoreException):
    '''No previously registred element found'''
    pass

class UndefinedSupportedTypesError(CoreException):
    '''Not definition of supported Resource types found'''
    pass
 
class NoResourceManagerForGivenType(CoreException):
    def __init__(self, rType):
        self._rType = rType

    def __str__(self):
        return repr(self._rType)