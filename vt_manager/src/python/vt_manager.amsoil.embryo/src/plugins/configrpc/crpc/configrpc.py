import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('configrpc')

xmlrpc = pm.getService('xmlrpc')
config = pm.getService("config")

class ConfigRPC(xmlrpc.Dispatcher):
    """
    """
    
    def __init__(self):
        super(ConfigRPC, self).__init__(logger)

    def ListConfigKeys(self):
        """
        Returns a list of config items:
        [ ..., [key, value, desc], ...]
        """
        result = []
        items = config.Config.loadAllConfigItems()
        for item in items:
            result.append([item.key, item.getValue(), item.desc])
        return result

    def ChangeConfig(self, key, value):
        item = config.Config.getConfigItem(key)
        item.write(value)