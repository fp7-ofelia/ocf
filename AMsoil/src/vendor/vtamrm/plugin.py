import amsoil.core.pluginmanager as pm
import utils.commonbase as cb

def setup():
# setup config keys
    config = pm.getService("config")
    config.install("vtam.max_reservation_duration", 4*60*60, "Maximum duration a VTAM resource (VM) can be held allocated (not provisioned).")
    config.install("vtam.max_vm_duration", 7*24*60*60, "Maximum duration a VTAM VM can be provisioned.")
    config.install("vtamrm.dbpath", cb.ENGINE, "Path to the vtam database.")	    
    config.install("vtam.allocated_vm_check_interval", 10*60, "Time between consecutive checks of the allocated expire time")
    config.install("vtam.created_vm_check_interval", 24*60*60, "Time between consecutive checks of the vm expire time")

    from vtresourcemanager import VTResourceManager
    import utils.vtexceptions as exceptions_package    
    rm = VTResourceManager()
    pm.registerService('vtresourcemanager', rm)
    pm.registerService('vtexceptions', exceptions_package)

    from vtadminresourcemanager import VTAdminResourceManager
    rm_admin = VTAdminResourceManager()
    pm.registerService('vtadminresourcemanager', rm_admin)
