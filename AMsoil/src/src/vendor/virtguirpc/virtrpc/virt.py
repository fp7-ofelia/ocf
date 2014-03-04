import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface
import amsoil.core.log
logger=amsoil.core.log.getLogger('virtguihandler')

xmlrpc = pm.getService('xmlrpc')

class VirtGUIHandler(xmlrpc.Dispatcher):
    
    def __init__(self):
        super(VirtGUIHandler, self).__init__(logger)
        self._delegate = None
    
    @serviceinterface
    def setDelegate(self, virtguidelegate):
        self._delegate = virtguidelegate
    
    @serviceinterface
    def getDelegate(self):
        return self._delegate
    
    def GetVersion(self):
        # no authentication necessary
        # delegate
        return self._delegate.get_version()

class VirtGUIDelegateBase(object):

    def __init__(self):
        super(VirtGUIDelegateBase, self).__init__()
        pass
    
    def get_version(self):
        return {
                'virtgui_api'                    : '1',
                'virtgui_api_versions'           : { '1' : '/gui' },
                }
