import amsoil.core.pluginmanager as pm
import utils.vtexceptions as vt_exception

'''@author: SergioVidiella'''

class VTAdminResourceManager(object):
    config = pm.getService("config")

    def __init__(self):
        super(VTAdminResourceManager, self).__init__()
