from vt_manager.controller.drivers.VTDriver import VTDriver
from vt_manager.models.XenServer import XenServer
from vt_manager.models.XenVM import XenVM
from vt_manager.models.VTServer import VTServer
from vt_manager.utils.HttpUtils import HttpUtils
import threading

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
            Server = XenServer.objects.get(uuid = action.server.uuid )
            VMmodel = Server.createVM(*XenDriver.xenVMtoModel(action.server.virtual_machines[0],threading.currentThread().callBackURL, save = True))
            return Server, VMmodel
        except Exception as e:
            raise e
	
    @staticmethod
    def createOrUpdateServerFromPOST(request, instance):
		#return XenServer.constructor(server.getName(),server.getOSType(),server.getOSDistribution(),server.getOSVersion(),server.getAgentURL(),save=True)
		server = XenServer.objects.get(uuid = instance.getUUID())
		if server:
			return server.updateServer(HttpUtils.getFieldInPost(request,VTServer, "name"),
				HttpUtils.getFieldInPost(request,VTServer, "operatingSystemType"),
				HttpUtils.getFieldInPost(request,VTServer, "operatingSystemDistribution"),
				HttpUtils.getFieldInPost(request,VTServer, "operatingSystemVersion"),
				HttpUtils.getFieldInPost(request,VTServer, "numberOfCPUs"),
				HttpUtils.getFieldInPost(request,VTServer, "CPUFrequency"),
				HttpUtils.getFieldInPost(request,VTServer, "memory"),
				HttpUtils.getFieldInPost(request,VTServer, "discSpaceGB"),
				HttpUtils.getFieldInPost(request,VTServer, "agentURL"),
				save=True)
		else:
			return XenServer.constructor(HttpUtils.getFieldInPost(request,VTServer, "name"),
							HttpUtils.getFieldInPost(request,VTServer, "operatingSystemType"),
							HttpUtils.getFieldInPost(request,VTServer, "operatingSystemDistribution"),
							HttpUtils.getFieldInPost(request,VTServer, "operatingSystemVersion"),
							HttpUtils.getFieldInPost(request,VTServer, "numberOfCPUs"),
							HttpUtils.getFieldInPost(request,VTServer, "CPUFrequency"),
							HttpUtils.getFieldInPost(request,VTServer, "memory"),
							HttpUtils.getFieldInPost(request,VTServer, "discSpaceGB"),
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
						instance.getNumberOfCPUs(),
						instance.getCPUFrequency(),
						instance.getMemory(),
						instance.getDiscSpaceGB(),
						instance.getAgentURL(),
						instance.getAgentPassword(),
						save = True)
		elif len(server)==0:
			return XenServer.constructor(instance.getName(),
								instance.getOSType(),
								instance.getOSDistribution(),
								instance.getOSVersion(),
								instance.getNumberOfCPUs(),
								instance.getCPUFrequency(),
								instance.getMemory(),
								instance.getDiscSpaceGB(),
								instance.getAgentURL(),
								instance.getAgentPassword(),
								save=True)
		else:
			raise Exception("Trying to create a server failed")

    @staticmethod
    def xenVMtoModel(VMxmlClass, callBackURL, save):
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
		# XXX
        callBackUrl = callBackURL
        hdSetupType = VMxmlClass.xen_configuration.hd_setup_type
        hdOriginPath = VMxmlClass.xen_configuration.hd_origin_path
        virtSetupType = VMxmlClass.xen_configuration.virtualization_setup_type
        return name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,None,None,callBackUrl,hdSetupType,hdOriginPath,virtSetupType,save

