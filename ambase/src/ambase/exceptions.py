class SliceAlreadyExists(Exception):
    pass

class AllocationError(Exception):
    pass

class ProvisionError(Exception):
    pass

class DeleteError(Exception):
    pass

class ShutDown(Exception):
    pass

class UnsupportedState(Exception):
    pass

class PerformOperationalStateError(Exception):
    pass