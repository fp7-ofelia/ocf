import copy
import uuid
import threading

from vt_manager.communication.utils.XmlHelper import XmlHelper, XmlCrafter
from vt_manager.models.VTServer import VTServer
from vt_manager.communication.sfa.vm_utils.Translator import Translator
from vt_manager.models.VirtualMachine import VirtualMachine

from vt_manager.utils.ServiceThread import ServiceThread
from vt_manager.utils.UrlUtils import UrlUtils

from vt_manager.controller.dispatchers.xmlrpc.ProvisioningDispatcher import ProvisioningDispatcher
from vt_manager.controller.dispatchers.xmlrpc.DispatcherLauncher import DispatcherLauncher

class VMSfaManager:

    '''Class to pass the VM parameters to an RSpec Instance for ProvisioningDisaptcher'''

    @staticmethod
    def getActionInstance(servers_slivers,projectName,sliceName):
	provisioningRSpecs = list()
	rspec = XmlHelper.getSimpleActionQuery()
	actionClassEmpty = copy.deepcopy(rspec.query.provisioning.action[0])
        actionClassEmpty.type_ = "create"
        rspec.query.provisioning.action.pop()
        for vms in servers_slivers:
	    server_id = vms['component_id']
	    for vm in vms['slivers']:
		server = VTServer.objects.get(uuid = server_id)
	        VMSfaManager.setDefaultVMParameters(vm,server,projectName,sliceName)
		actionClass = copy.deepcopy(actionClassEmpty)
                actionClass.id = uuid.uuid4()
                Translator.VMdictToClass(vm, actionClass.server.virtual_machines[0])
		Translator.VMdicIfacesToClass(vm['interfaces'],actionClass.server.virtual_machines[0].xen_configuration.interfaces)
                actionClass.server.uuid = server_id
                actionClass.server.virtualization_type = server.getVirtTech()
                rspec.query.provisioning.action.append(actionClass)
		provisioningRSpecs.append(rspec.query.provisioning)

	return provisioningRSpecs
	
    @staticmethod
    def setDefaultVMParameters(vm,server,projectName,sliceName):
        VM = VirtualMachine.objects.filter(projectName = projectName)
	if VM:
		vm['project-id'] = VM[0].projectId
	else:
		vm['project-id'] = str(uuid.uuid4())	

	vm['project-name'] = projectName
	
	vm['slice-id'] = None
	for virmach in VM:
		if virmach.sliceName == sliceName:
			vm['slice-id'] = virmach.sliceId

	if not vm['slice-id']:
		vm['slice-id'] = str(uuid.uuid4()) 

	vm['slice-name']= sliceName	 
	vm['uuid'] = str(uuid.uuid4())
        vm['state'] = "on queue"
        #assign same virt technology as the server where vm created
        vm['virtualization-type'] = server.getVirtTech()
	vm['server-id'] = server.getUUID()
        vm['aggregate-id'] = 'aggregate-id'
        #assign parameters according to selected disc image
        vm['operating-system-type'] = 'GNU/Linux'
        vm['operating-system-version'] = '6.0'
        vm['operating-system-distribution'] = 'Debian'
        vm['hd-origin-path'] = "legacy/legacy.tar.gz"

	return vm
 
