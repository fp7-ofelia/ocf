import amsoil.core.pluginmanager as pm

def setup():
    # setup config keys

    from dummyresourcemanager import DummyResourceManager
    import dummyexceptions as exceptions_package    
    rm = DummyResourceManager()
    pm.registerService('dummyresourcemanager', rm)
    pm.registerService('dummyexceptions', exceptions_package)
    
