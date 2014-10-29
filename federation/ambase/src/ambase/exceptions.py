class SliceAlreadyExists(Exception):
    pass

class AllocationError(Exception):
    pass

class ProvisionError(Exception):
    pass

class DeleteError(Exception):
    pass

class Shutdown(Exception):
    pass

class UnsupportedState(Exception):
    pass

class PerformOperationalStateError(Exception):
    pass

class ApiErrorException(Exception):
    def __init__(self, code, output):
        self.code = code
        self.output = output

    def __str__(self):
        return "ApiError(%r, %r)" % (self.code, self.output)
