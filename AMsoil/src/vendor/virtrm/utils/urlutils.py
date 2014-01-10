import amsoil.core.pluginmanager as pm

class UrlUtils(): 
    @staticmethod
    def add_path_to_own_url(path):
        config = pm.getService("config")
        path = str(path)
        return "https://%s:%s@%s:%s%s" % (
                                             config.get("virtrm.CALLBACK_GUI_USER"), config.get("virtrm.CALLBACK_GUI_PASSWORD"),
                                             config.get("virtrm.CALLBACK_VTAM_IP"), config.get("virtrm.CALLBACK_VTAM_PORT"),
                                             path,
                                          )
        
    @staticmethod
    def get_own_callback_url():
        return UrlUtils.add_path_to_own_url("/xmlrpc/agent")
