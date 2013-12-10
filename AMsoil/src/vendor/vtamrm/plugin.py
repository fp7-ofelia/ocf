import amsoil.core.pluginmanager as pm

def setup():
# setup config keys
    config = pm.getService("config")
    
    # Read settings
    from settings import local
    print "Loading settings...."
    for setting in local.__dict__:
        # Retrieve user-defined settings (avoid internal ones - '__')
        if not setting.startswith("__"):
            print "%s => %s" % (setting, local.__dict__[setting])
            config.install("vtamrm.%s" % setting, local.__dict__[setting], "")

    from vtresourcemanager import VTResourceManager
    import utils.vtexceptions as exceptions_package
    rm = VTResourceManager()
    pm.registerService('vtresourcemanager', rm)
    pm.registerService('vtexceptions', exceptions_package)

    from vtadminresourcemanager import VTAdminResourceManager
    rm_admin = VTAdminResourceManager()
    pm.registerService('vtadminresourcemanager', rm_admin)
