from amsoil.core.exception import CoreException

class SliverTypeNotSupportedError(CoreException):
    def __init__(self, sType):
        self._sType = sType

    def __str__(self):
        return repr(self._sType)

class MalformedRSpec3Error(CoreException):
    def __init__(self, comment):
        self._comment = comment

    def __str__(self):
        return repr(self._comment)
