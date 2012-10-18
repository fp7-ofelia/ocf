from amsoil.core.exception import CoreException

class QueueAlreadyDeclared(CoreException):
    '''
    QueueAlreadyDeclared
    '''
    pass

class QueueDoesNotExist(CoreException):
    '''
    QueueDoesNotExist
    '''
    pass

class InvalidCallback(CoreException):
    '''
    InvalidCallback
    '''
    pass

class CallbackAlreadyRegistered(CoreException):
    '''
    CallbackAlreadyRegistered
    '''
    pass
