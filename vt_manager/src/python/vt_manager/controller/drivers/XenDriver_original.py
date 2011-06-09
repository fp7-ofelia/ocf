from vt_manager.controller.drivers.VTDriver import VTDriver
from vt_manager.models.XenServer import XenServer
from vt_manager.models.XenVM import XenVM
from vt_manager.models.VTServer import VTServer
from vt_manager.utils.HttpUtils import HttpUtils

class XenDriver(VTDriver):


	def __init__(self):
		self.ServerClass = eval('XenServer') 
		self.VMclass = eval('XenVM') 


	@staticmethod
	def getInstance():
		return XenDriver()

	def deleteVM(vm):
		try:
			vm.Server.get().deleteVM(vm)
		except:
			raise	

	def getServerAndCreateVM(self,action):
       
		try: 
			Server = self.ServerClass.objects.get(uuid = action.virtual_machine.server_id )
			VMmodel = Server.createVM(Translator.xenVMtoModel(action.virtual_machine,threading.currentThread().callBackURL, save = True))
			return Server, VMmodel
		except:
			raise
	
	@staticmethod
	def createOrUpdateServerFromPOST(request, instance):
		#return XenServer.constructor(server.getName(),server.getOSType(),server.getOSDistribution(),server.getOSVersion(),server.getAgentURL(),save=True)
		server = XenServer.objects.get(uuid = instance.getUUID())
		if server:
			return server.update(HttpUtils.getFieldInPost(request,VTServer, "name"),
				HttpUtils.getFieldInPost(request,VTServer, "operatingSystemType"),
				HttpUtils.getFieldInPost(request,VTServer, "operatingSystemDistribution"),
				HttpUtils.getFieldInPost(request,VTServer, "operatingSystemVersion"),
				HttpUtils.getFieldInPost(request,VTServer, "agentURL"),
				save=True)
		else:
			return XenServer.constructor(HttpUtils.getFieldInPost(request,VTServer, "name"),
									HttpUtils.getFieldInPost(request,VTServer, "operatingSystemType"),
									HttpUtils.getFieldInPost(request,VTServer, "operatingSystemDistribution"),
									HttpUtils.getFieldInPost(request,VTServer, "operatingSystemVersion"),
									HttpUtils.getFieldInPost(request,VTServer, "agentURL"),
									save=True)
		
