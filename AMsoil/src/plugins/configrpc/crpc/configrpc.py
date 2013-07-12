import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('configrpc')

xmlrpc = pm.getService('xmlrpc')
config = pm.getService("config")

# TODO IMPORTANT: add authentication / authorization here

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
        items = config.getAll()
        for item in items:
            result.append([item['key'], item['value'], item['description']])
        return result

    def ChangeConfig(self, key, value):
        item = config.set(key, value)