from controller.drivers.vtdriver import VTDriver
from resources.xenserver import XenServer
from resources.xenvm import XenVM
from resources.vtserver import VTServer
from utils.httputils import HttpUtils
import threading

from utils.commonbase import DB_SESSION
import amsoil.core.log

logging=amsoil.core.log.getLogger('XenDriver')

class XenDriver(VTDriver):


#	def __init__(self):
#		self.ServerClass = eval('XenServer') 
#		self.VMclass = eval('XenVM') 


	@staticmethod
	def getInstance():
		return XenDriver()

	def deleteVM(self, vm):
		try:
			vm.Server.get().deleteVM(vm)
		except:
			raise	

	def getServerAndCreateVM(self,action):
       
		try: 
			logging.debug("*************************** GO 1")
			Server = DB_SESSION.query(VTServer).filter(VTServer.uuid == action.server.uuid).one().xenserver
			logging.debug("*************************** GO 2")
			VMmodel = Server.createVM(XenDriver.xenVMtoModel(action.server.virtual_machines[0],threading.currentThread().callBackURL, save = True))
			logging.debug("*************************** GO 3")
			return Server, VMmodel
		except:
			raise
	
	@staticmethod
	def createOrUpdateServerFromPOST(request, instance):
		#return XenServer.constructor(server.getName(),server.getOSType(),server.getOSDistribution(),server.getOSVersion(),server.getAgentURL(),save=True)
		server = XenServer.objects.get(uuid = instance.getUUID())
		if server:
			return server.updateServer(HttpUtils.getFieldInPost(request,VTServer, "name"),
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
		
	def crudServerFromInstance(self,instance):
		server = XenServer.objects.filter(uuid = instance.getUUID())
		if len(server)==1:
			server = server[0]
			return server.updateServer(instance.getName(),
						instance.getOSType(),
						instance.getOSDistribution(),
						instance.getOSVersion(),
						instance.getAgentURL(),
						instance.getAgentPassword(),
						save = True)
		elif len(server)==0:
			return XenServer.constructor(instance.getName(),
								instance.getOSType(),
								instance.getOSDistribution(),
								instance.getOSVersion(),
								instance.getAgentURL(),
								instance.getAgentPassword(),
								save=True)
		else:
			raise Exception("Trying to create a server failed")

	@staticmethod
	def xenVMtoModel(VMxmlClass, callBackURL, save):
		logging.debug("************************************** THIS OK 1")
		name = VMxmlClass.name
		uuid = VMxmlClass.uuid
		projectId = VMxmlClass.project_id
		projectName = VMxmlClass.project_name
		sliceId = VMxmlClass.slice_id
		sliceName = VMxmlClass.slice_name
		osType = VMxmlClass.operating_system_type
		osVersion = VMxmlClass.operating_system_version
		osDist = VMxmlClass.operating_system_distribution
		memory = VMxmlClass.xen_configuration.memory_mb
		callBackUrl = callBackURL
		hdSetupType = VMxmlClass.xen_configuration.hd_setup_type
		hdOriginPath = VMxmlClass.xen_configuration.hd_origin_path
		virtSetupType = VMxmlClass.xen_configuration.virtualization_setup_type
		logging.debug("************************************** THIS OK 2")
		return name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,None,None,callBackUrl,hdSetupType,hdOriginPath,virtSetupType,save

