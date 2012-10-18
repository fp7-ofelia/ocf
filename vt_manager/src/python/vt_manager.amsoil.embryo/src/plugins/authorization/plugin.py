import amsoil.core.pluginmanager as pm

def setup():
    import auth
    pm.registerService("authorization", auth)
