from vt_manager.models.Action import Action

class ActionController():
	
	@staticmethod
	def getAction(uuid):
		return Actions.objects.get(uuid=uuid)
	
	@staticmethod
	def createNewAction(aType,status,objectUUID=None,description=""):
		return Action.constructor(aType,status,objectUUID,description)	
