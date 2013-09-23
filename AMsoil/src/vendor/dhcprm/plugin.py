import amsoil.core.pluginmanager as pm

def setup():
    # setup config keys
    config = pm.getService("config")
    config.install("dhcprm.max_reservation_duration", 10*60, "Maximum duration a DHCP resource can be held allocated (not provisioned).")
    config.install("dhcprm.max_lease_duration", 24*60*60, "Maximum duration DHCP lease can be provisioned.")
    config.install("dhcprm.dbpath", "deploy/dhcp.db", "Path to the dhcp database (if relative, AMsoil's root will be assumed).")
    
    from dhcpresourcemanager import DHCPResourceManager
    import dhcpexceptions as exceptions_package
    rm = DHCPResourceManager()
    pm.registerService('dhcpresourcemanager', rm)
    pm.registerService('dhcpexceptions', exceptions_package)
    