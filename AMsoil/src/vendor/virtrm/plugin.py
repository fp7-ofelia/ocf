import amsoil.core.pluginmanager as pm

def setup():
    # Setup config keys
    config = pm.getService("config")
    # Read settings
    from settings import local
    for setting in local.__dict__:
        # Retrieve user-defined settings (avoid internal ones - '__')
        if not setting.startswith("__"):
            config.install("virtrm.%s" % setting, local.__dict__[setting], "")
    # Register Virtualisation RM as a service
    from managers.base import VTResourceManager
    import utils.exceptions as exceptions_package
    rm = VTResourceManager()
    pm.registerService('virtrm', rm)
    pm.registerService('virtexceptions', exceptions_package)
    # Register Virtualisation Admin RM as a service
    from managers.admin import VTAdminResourceManager
    rm_admin = VTAdminResourceManager()
    pm.registerService('virtadminrm', rm_admin)
