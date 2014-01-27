from vt_manager.models.MacRange import MacRange
from vt_manager.models.MacSlot import MacSlot

class EthernetController():
	
	@staticmethod
	def listRanges(filterEnabled=False):
		
		if not filterEnabled:
			return MacRange.objects.all()
		else:
			return MacRange.objects.filter(enabled=True) 
	
	@staticmethod
	def createRange(instance):
		obj = MacRange.constructor(instance.getName(),instance.getStartMac(),instance.getEndMac(),instance.getIsGlobal())
		return obj
	
	@staticmethod
	def deleteRange(rangeId):
		obj = EthernetController.getRange(rangeId)
		obj.destroy()
		return obj
	
	@staticmethod
	def getRange(rangeId):
		return MacRange.objects.get(id = rangeId)
	
	@staticmethod
	def addExcludedMac(instance,request):
		instance.addExcludedMac(request.POST["mac"],request.POST["comment"])
	@staticmethod
	def removeExcludedMac(instance,macId):
		obj = MacSlot.objects.get(id = macId)
		#instance.removeExcludedMac(obj)
		obj.destroy()
