#from vt_manager.settings.settingsLoader import settings.ROOT_USERNAME,settings.ROOT_PASSWORD,settings.CALLBACK_VTAM_IP,settings.CALLBACK_VTAM_PORT
#from django.conf import settings

import amsoil.core.pluginmanager as pm


class UrlUtils():
	
	@staticmethod
	def addPathToOwnURL(path):
		config = pm.getService("config")
		path = str(path)
		return "https://"+config.get("vtamrm.CALLBACK_GUI_USER")+":"+config.get("vtamrm.CALLBACK_GUI_PASSWORD")+"@"+config.get("vtamrm.CALLBACK_VTAM_IP")+":"+config.get("vtamrm.CALLBACK_VTAM_PORT")+path
	
	@staticmethod
	def getOwnCallbackURL():
		return UrlUtils.addPathToOwnURL("/xmlrpc/agent")
