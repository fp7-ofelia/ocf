from vt_manager.settings.settingsLoader import ROOT_USERNAME,ROOT_PASSWORD,VTAM_IP,VTAM_PORT

class UrlUtils():
	
	@staticmethod
	def addPathToOwnURL(path):

		path = str(path)
		return "https://"+ROOT_USERNAME+":"+ROOT_PASSWORD+"@"+VTAM_IP+":"+VTAM_PORT+path
	
	@staticmethod
	def getOwnCallbackURL():
		return UrlUtils.addPathToOwnURL("/xmlrpc/agent")
