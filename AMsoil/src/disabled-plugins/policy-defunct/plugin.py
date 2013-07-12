import amsoil.core.pluginmanager as pm


def setup():
    from policymanager import PolicyManager
    pm.registerService('policy', PolicyManager)
