from virtrmutils import VirtUtils
import amsoil.core.pluginmanager as pm

def setup():
    pm.registerService("virtutils", VirtUtils)
