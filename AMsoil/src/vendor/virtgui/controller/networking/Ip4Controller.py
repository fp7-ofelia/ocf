from vt_manager.models.Ip4Range import Ip4Range
from vt_manager.models.Ip4Slot import Ip4Slot

class Ip4Controller():
	
	@staticmethod
	def listRanges(filterEnabled=False):
		
		if not filterEnabled:
			return Ip4Range.objects.all()
		else:
			return Ip4Range.objects.filter(enabled=True) 
	
	@staticmethod
	def createRange(instance):
		obj = Ip4Range.constructor(instance.getName(),instance.getStartIp(),instance.getEndIp(),instance.getNetmask(),instance.getGatewayIp(),instance.getDNS1(),instance.getDNS2(),instance.getIsGlobal())
		return obj
	
	@staticmethod
	def deleteRange(rangeId):
		obj = Ip4Controller.getRange(rangeId)
		obj.destroy()
		return obj
	
	@staticmethod
	def getRange(rangeId):
		return Ip4Range.objects.get(id = rangeId)
	
	@staticmethod
	def addExcludedIp4(instance,request):
		instance.addExcludedIp(request.POST["ip"],request.POST["comment"])
	@staticmethod
	def removeExcludedIp4(instance,ip4Id):
		obj = Ip4Slot.objects.get(id = ip4Id)
		#instance.removeExcludedIp(obj)
		obj.destroy()
