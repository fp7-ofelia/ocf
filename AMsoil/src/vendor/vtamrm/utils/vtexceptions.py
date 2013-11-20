from amsoil.core.exception import CoreException

class VTAMException(CoreException):
    def __init__(self, desc):
        self._desc = desc
    def __str__(self):
        return "VTAM: %s" % (self._desc,)

class VTAMIpNotFound(VTAMException):
    def __init__(self, ip):
        super(VTAMIpNotFound, self).__init__("Ip not found (%s)" % (ip,))

class VTAMIpAlreadyTaken(VTAMException):
    def __init__(self, ip):
        super(VTAMIpAlreadyTaken, self).__init__("Ip is already taken (%s)" % (ip,))

class VTAMMaxVmDurationExceeded(VTAMException):
    def __init__(self, vm):
        super(VTAMMaxVmDurationExceeded, self).__init__("Desired lease duration is too far in the future (%s)" % (vm,))

class VTAMMacNotFound(VTAMException):
    def __init__(self, mac):
	super(VTAMMacNotFound, self).__init__("Mac not found (%s)" % (mac,))

class VTAMMacAlreadyTaken(VTAMException):
    def __init__(self, mac):
	super(VTAMMacAlreadyTaken, self).__init__("Mac is already taken (%s)" % (mac,))

class VTAMVmNameAlreadyTaken(VTAMException):
    def __init__(self, vm):
	vm_name = vm
	super(VTAMVmNameAlreadyTaken, self).__init__("VM name is already taken (%s)" % (vm,)) 

class VTAMInterfaceNotFound(VTAMException):
    def __init__(self, interface):
	super(VTAMInterfaceNotFound, self).__init__("Interface not found (%s)" % (interface,))

class VTAMServerNotFound(VTAMException):
    def __init__(self, server):
	super(VTAMServerNotFound, self).__init__("Server not found (%s)" % (server,))

class VTMaxVMDurationExceeded(VTAMException):
    def __init__(self, vm, time=None):
	super(VTMaxVMDurationExceeded, self).__init__("Max reservation duration exceeded (%s %s)" % (vm, time))

class VTAMMalformedUrn(VTAMException):
    def __init__(self, urn):
	super(VTAMMalformedUrn, self).__init__("The urn hasn't the expected format (%s)" % (urn,))

class VTAMNoSliversInSlice(VTAMException):
    def __init__(self, urn):
	super(VTAMNoSliversInSlice, self).__init__("The given slice don't have any vm (%s)" % (urn,))

class VTAMVMNotFound(VTAMException):
    def __init__(self, urn):
	super(VTAMVMNotFound, self).__init__("The given urn doesn't correspond to any vm (%s)" % (urn,))

class VTAMNoVMsInSlice(VTAMException):
    def __init__(self, urn):
	super(VTAMNoVMsInSlice, self).__init__("The given slice doesn't contain any vm (%s)" %(urn,))
