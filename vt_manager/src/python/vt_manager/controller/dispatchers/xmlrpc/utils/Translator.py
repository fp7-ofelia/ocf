from vt_manager.models import *

from vt_manager.models.Action import Action
import copy
import uuid

class Translator():

#    @staticmethod
#    def VMtoModel(VMxmlClass, callBackURL , save = "noSave"):
#        VMmodel = VM()
#        VMmodel.setUUID(uuid.uuid4())
#        VMmodel.setCallBackURL(callBackURL)
#        VMmodel.setName(VMxmlClass.name)
#        VMmodel.setUUID(VMxmlClass.uuid)
#        VMmodel.setProjectId(VMxmlClass.project_id)
#        VMmodel.setSliceId(VMxmlClass.slice_id)
#        VMmodel.setProjectName(VMxmlClass.project_name)
#        VMmodel.setSliceName(VMxmlClass.slice_name)
#        VMmodel.setOStype(VMxmlClass.operating_system_type)
#        VMmodel.setOSversion(VMxmlClass.operating_system_version)
#        VMmodel.setOSdist(VMxmlClass.operating_system_distribution)
#        VMmodel.setVirtTech(VMxmlClass.virtualization_type)
#        VMmodel.setServerID(VMxmlClass.server_id)
#        VMmodel.setHDsetupType(VMxmlClass.xen_configuration.hd_setup_type)
#        VMmodel.setHDoriginPath(VMxmlClass.xen_configuration.hd_origin_path) 
#        VMmodel.setVirtualizationSetupType(VMxmlClass.xen_configuration.virtualization_setup_type)
#        VMmodel.setMemory(VMxmlClass.xen_configuration.memory_mb)
#        #If the translation is doing just when the VM is created it is ok to set its state to unknow here
#        VMmodel.setState("on queue")
#        if save is "save":
#            VMmodel.save()
#        return VMmodel
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
		callBackUrl = callBackURL
		hdSetupType = VMxmlClass.xen_configuration.hd_setup_type
		print "[LEODEBUG] HD SETUP TYPE EN TRANSLATOR"
		print VMxmlClass.xen_configuration.hd_setup_type
		hdOriginPath = VMxmlClass.xen_configuration.hd_origin_path
		virtSetupType = VMxmlClass.xen_configuration.virtualization_setup_type
		return name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,None,None,callBackUrl,hdSetupType,hdOriginPath,virtSetupType,save

	@staticmethod
	def ActionToModel(action, hyperaction, save = "noSave" ):
		actionModel = Action()
		actionModel.hyperaction = hyperaction
		if not action.status:
			actionModel.status = 'QUEUED'
		else:
			actionModel.status = action.status
		actionModel.type = action.type_
		actionModel.uuid = action.id
		if save is "save":
			actionModel.save()
		return actionModel

	@staticmethod
	def ServerModelToClass(sModel, sClass ):
		sClass.name = sModel.getName()
		#XXX: CHECK THIS
		sClass.id = sModel.id
		sClass.uuid = sModel.getUUID()
		sClass.operating_system_type = sModel.getOSType()
		sClass.operating_system_distribution = sModel.getOSDistribution()
		sClass.operating_system_version = sModel.getOSVersion()
		sClass.virtualization_type = sModel.getVirtTech()
		ifaces = sModel.getNetworkInterfaces()
		for ifaceIndex, iface in enumerate(ifaces):
			if ifaceIndex != 0:
				newInterface = copy.deepcopy(sClass.interfaces.interface[0])
				sClass.interfaces.interface.append(newInterface)
			if iface.isMgmt:
				sClass.interfaces.interface[ifaceIndex].ismgmt = True
			else:
				sClass.interfaces.interface[ifaceIndex].ismgmt = False
			sClass.interfaces.interface[ifaceIndex].name = iface.name   
			sClass.interfaces.interface[ifaceIndex].switch_id= iface.switchID   
			sClass.interfaces.interface[ifaceIndex].switch_port = iface.port  
	#	mgmtInterface = copy.deepcopy(sClass.interfaces.interface[0])
	#	mgmtInterface.name = "NONE"
	#	mgmtInterface.switch_id= sModel.getVmMgmtIface() 
	#	mgmtInterface.switch_port = "NONE"
	#	mgmtInterface.ismgmt = True
	#	sClass.interfaces.interface.append(mgmtInterface)
 
	@staticmethod
	def VMmodelToClass(VMmodel, VMxmlClass):

		VMxmlClass.name = VMmodel.getName()
		VMxmlClass.uuid = VMmodel.getUUID()
		VMxmlClass.project_id = VMmodel.getProjectId()
		VMxmlClass.slice_id = VMmodel.getSliceId()
		VMxmlClass.project_name = VMmodel.getProjectName()
		VMxmlClass.slice_name = VMmodel.getSliceName()
		VMxmlClass.operating_system_type = VMmodel.getOSType()
		VMxmlClass.operating_system_version = VMmodel.getOSVersion()
		VMxmlClass.operating_system_distribution = VMmodel.getOSDistribution()
		#VMxmlClass.virtualization_type = VMmodel.getVirtTech()
		#VMxmlClass.server_id = VMmodel.getServerID()
		VMxmlClass.xen_configuration.hd_setup_type = VMmodel.getHdSetupType()
		VMxmlClass.xen_configuration.hd_origin_path = VMmodel.getHdOriginPath()
		VMxmlClass.xen_configuration.virtualization_setup_type = VMmodel.getVirtualizationSetupType()
		VMxmlClass.xen_configuration.memory_mb = VMmodel.getMemory()
		             
		#XXX: It is important the order the ifaces are scanned. It should be first the dataIfaces and then the mgmt one.
		vmInterfaces = VMmodel.networkInterfaces.all()
		serverDataIfaces = VTServer.objects.get(uuid = VMmodel.getServerID()).ifaces.all()
		baseIface = copy.deepcopy(VMxmlClass.xen_configuration.interfaces.interface[0])
		for interface in serverDataIfaces:
			print "SERVER IFACE: %s" %interface.ifaceName 
		for ifaceIndex, serverDataIface in enumerate(serverDataIfaces):
			try:
				#XXX: This way of calling the MACs comes from the setVMinterfaces, considering that the interfaces in the VM will be always eth0,1,...
				# maybe this should be changed
				mac = macs.get(ifaceName = 'eth'+str(ifaceIndex+1))
				print "Copiando %s" %mac.ifaceName
				if (ifaceIndex != 0):
					newInterface = copy.deepcopy(baseIface)
					VMxmlClass.xen_configuration.interfaces.interface.append(newInterface)
				VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].name = mac.ifaceName
				VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].ismgmt = None
				VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].ip = None
				VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].mask = None
				VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].gw = None
				VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].dns1 = None
				VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].dns2 = None
				VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].switch_id = serverDataIfaces[ifaceIndex].ifaceName
				VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].mac = mac.mac
			except:
				print "[Warning]: There is not corresponding MAC in the VM for a Server's dataIface"
				pass

		#MGMT IFACE
		print "mgmt IFACE en VM %s" %VMmodel.name
		print "first len: %d" %len(VMxmlClass.xen_configuration.interfaces.interface)
		newInterface = copy.deepcopy(baseIface)
		print "second len: %d" %len(VMxmlClass.xen_configuration.interfaces.interface)
		VMxmlClass.xen_configuration.interfaces.interface.append(newInterface)
		print "third len: %d" %len(VMxmlClass.xen_configuration.interfaces.interface)
		mgmtMac = macs.get(isMgmt = 1)
		newInterface.name = mgmtMac.ifaceName
		print mgmtMac.ifaceName
		newInterface.ismgmt='True'
		newInterface.ip = VMmodel.ips.get().ip
		newInterface.mask = VMmodel.ips.get().mask
		newInterface.gw = VMmodel.ips.get().gw
		newInterface.dns1 = VMmodel.ips.get().dns1
		newInterface.dns2 = VMmodel.ips.get().dns2
		newInterface.switch_id = VTServer.objects.get(uuid = VMmodel.getServerID()).getVmMgmtIface()
		newInterface.mac = mgmtMac.mac
		#VMxmlClass.xen_configuration.interfaces.interface.append(newInterface)

