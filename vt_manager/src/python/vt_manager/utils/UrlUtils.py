#from vt_manager.settings.settingsLoader import settings.ROOT_USERNAME,settings.ROOT_PASSWORD,settings.VTAM_IP,settings.VTAM_PORT
from django.conf import settings

class UrlUtils():
	
	@staticmethod
	def addPathToOwnURL(path):

		path = str(path)
		return "https://"+settings.ROOT_USERNAME+":"+settings.ROOT_PASSWORD+"@"+settings.VTAM_IP+":"+settings.VTAM_PORT+path
	
	@staticmethod
	def getOwnCallbackURL():
		return UrlUtils.addPathToOwnURL("/xmlrpc/agent")
