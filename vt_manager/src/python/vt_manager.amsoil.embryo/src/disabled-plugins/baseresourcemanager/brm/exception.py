from amsoil.core.exception import CoreException

class UnknownResourceTypeError(CoreException):
    pass
class InvalidStateError(CoreException):
    pass
class UnknownReservationStateError(CoreException):
    pass
class UnknownDateTimeFormatError(CoreException):
    pass

