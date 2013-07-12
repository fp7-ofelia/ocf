from amsoil.core.exception import CoreException
        
class DHCPException(CoreException):
    def __init__(self, desc):
        self._desc = desc
    def __str__(self):
        return "DHCP: %s" % (self._desc,)

class DHCPLeaseNotFound(DHCPException):
    def __init__(self, ip):
        super(DHCPLeaseNotFound, self).__init__("Lease not found (%s)" % (ip,))

class DHCPLeaseAlreadyTaken(DHCPException):
    def __init__(self, ip):
        super(DHCPLeaseAlreadyTaken, self).__init__("Lease is already taken (%s)" % (ip,))

class DHCPMaxLeaseDurationExceeded(DHCPException):
    def __init__(self, ip):
        super(DHCPMaxLeaseDurationExceeded, self).__init__("Desired lease duration is too far in the future (%s)" % (ip,))
