from amsoil.core.exception import CoreException

class VirtException(CoreException):
    def __init__(self, desc):
        self._desc = desc
    def __str__(self):
        return "Virt: %s" % (self._desc,)

class VirtIpNotFound(VirtException):
    def __init__(self, ip):
        super(VirtIpNotFound, self).__init__("IP not found (%s)" % (ip,))

class VirtIpAlreadyTaken(VirtException):
    def __init__(self, ip):
        super(VirtIpAlreadyTaken, self).__init__("IP already taken (%s)" % (ip,))

class VirtMaxVmDurationExceeded(VirtException):
    def __init__(self, vm):
        super(VirtMaxVmDurationExceeded, self).__init__("Desired lease duration is too far in the future (%s)" % (vm,))

class VirtMacNotFound(VirtException):
    def __init__(self, mac):
	super(VirtMacNotFound, self).__init__("MAC not found (%s)" % (mac,))

class VirtMacAlreadyTaken(VirtException):
    def __init__(self, mac):
	super(VirtMacAlreadyTaken, self).__init__("MAC already taken (%s)" % (mac,))

class VirtVmNameAlreadyTaken(VirtException):
    def __init__(self, vm):
	vm_name = vm
	super(VirtVmNameAlreadyTaken, self).__init__("VM name already taken (%s)" % (vm,)) 

class VirtInterfaceNotFound(VirtException):
    def __init__(self, interface):
	super(VirtInterfaceNotFound, self).__init__("Interface not found (%s)" % (interface,))

class VirtServerNotFound(VirtException):
    def __init__(self, server):
	super(VirtServerNotFound, self).__init__("Server not found (%s)" % (server,))

class VirtMaxVMDurationExceeded(VirtException):
    def __init__(self, vm, time=None):
	super(VirtMaxVMDurationExceeded, self).__init__("Max reservation duration exceeded (%s %s)" % (vm, time))

class VirtMalformedUrn(VirtException):
    def __init__(self, urn):
	super(VirtMalformedUrn, self).__init__("The URN has not the expected format (%s)" % (urn,))

class VirtNoSliversInSlice(VirtException):
    def __init__(self, urn):
	super(VirtNoSliversInSlice, self).__init__("The given slice does not have any VM (%s)" % (urn,))

class VirtVMNotFound(VirtException):
    def __init__(self, urn):
	super(VirtVMNotFound, self).__init__("The given URN does not correspond to any VM (%s)" % (urn,))

class VirtNoVMsInSlice(VirtException):
    def __init__(self, urn):
	super(VirtNoVMsInSlice, self).__init__("The given slice does not contain any VM (%s)" %(urn,))

class VirtContainerDuplicated(VirtException):
    def __init__(self, urn):
        super(VirtContainerDuplicated, self).__init__("The given slice is duplicated" %(urn,))
