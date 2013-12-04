import amsoil.core.pluginmanager as pm

def setup():
# setup config keys
    config = pm.getService("config")
    #Reservation time configuration
    config.install("vtam.max_reservation_duration", 4*60*60, "Maximum duration a VTAM resource (VM) can be held allocated (not provisioned).")
    config.install("vtam.allocated_vm_check_interval", 10*60, "Time between consecutive checks of the allocated expire time")
    config.install("vtam.created_vm_check_interval", 24*60*60, "Time between consecutive checks of the vm expire time")
    config.install("vtam.max_vm_duration", 7*24*60*60, "Maximum duration a VTAM VM can be provisioned.")
    #VTAM database configuration
    config.install("vtamrm.database_engine", "mysql", "The database engine, mysql, prostgresql, sqlite,...")
    config.install("vtamrm.database_user", "root", "The database root username")
    config.install("vtamrm.database_password", "ofelia4you", "The database password") 
    config.install("vtamrm.database_host", "127.0.0.1", "The host where the database is allocated")
    config.install("vtamrm.database_name", "vt_am879544567", "The name of the VTAM database")
    #email configuration    
    config.install("vtamrm.default_from_email", "OFELIA-noreply@fp7-ofelia.eu", "The default email sender")
    config.install("vtamrm.email_subject_prefix", "[OFELIA CF] ", "The email subject prefix")
    config.install("vtamrm.email_use_tls", True, "")
    config.install("vtamrm.email_host_user", "", "")
    config.install("vtamrm.email_host_password", "", "")
    config.install("vtamrm.email_port", 25, "The email default port")
    #callbackurl configuration
    config.install("vtamrm.callback_root_username", "", "")
    config.install("vtamrm.callback_root_password", "", "")
    config.install("vtamrm.callback_ip", "", "")
    config.install("vtamrm.callback_port", "", "")

    from vtresourcemanager import VTResourceManager
    import utils.vtexceptions as exceptions_package    
    rm = VTResourceManager()
    pm.registerService('vtresourcemanager', rm)
    pm.registerService('vtexceptions', exceptions_package)

    from vtadminresourcemanager import VTAdminResourceManager
    rm_admin = VTAdminResourceManager()
    pm.registerService('vtadminresourcemanager', rm_admin)
