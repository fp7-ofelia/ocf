from ambase.config.terms import TERMS_CONDITIONS_URL

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

class TermsNotAccepted(Exception):
    def __init__(self, code, output=None):
        self.code = code
        self.output = "[T&C-APPROVAL-MISSING] Approval of the Terms & Conditions is required in order to use this testbed. Please visit %s" % TERMS_CONDITIONS_URL

    def __str__(self):
        return self.output

class ApiErrorException(Exception):
    def __init__(self, code, output):
        self.code = code
        self.output = output

    def __str__(self):
        return "ApiError(%r, %r)" % (self.code, self.output)
