import amsoil.core.pluginmanager as pm

class UrlUtils():
	
	@staticmethod
	def addPathToOwnURL(path):
		config = pm.getService("config")
		path = str(path)
		return "https://%s:%s@%s:%s%s" % (
								config.get("virtrm.CALLBACK_GUI_USER"), config.get("virtrm.CALLBACK_GUI_PASSWORD"),
								config.get("virtrm.CALLBACK_VTAM_IP"), config.get("virtrm.CALLBACK_VTAM_PORT"),
								path,
								)
	
	@staticmethod
	def getOwnCallbackURL():
		return UrlUtils.addPathToOwnURL("/xmlrpc/agent")
