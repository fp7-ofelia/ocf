#from vt_manager.settings.settingsLoader import settings.ROOT_USERNAME,settings.ROOT_PASSWORD,settings.VTAM_IP,settings.VTAM_PORT
#from django.conf import settings

import amsoil.core.pluginmanager as pm


class UrlUtils():
	
	@staticmethod
	def addPathToOwnURL(path):
		config = pm.getService("config")
		path = str(path)
		return "https://"+config.get("vtamrm.callback_root_username")+":"+config.get("vtamrm.callback_root_password")+"@"+config.get("vtamrm.callback_ip")+":"+config.get("vtamrm.callback_port")+path
	
	@staticmethod
	def getOwnCallbackURL():
		return UrlUtils.addPathToOwnURL("/xmlrpc/agent")
