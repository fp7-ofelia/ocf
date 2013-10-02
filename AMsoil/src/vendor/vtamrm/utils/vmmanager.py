import copy
import uuid
import threading

from resources.vtserver import VTServer
from resources.virtualmachine import VirtualMachine

from utils.xmlhelper import XmlHelper, XmlCrafter
from utils.translator import Translator
from utils.servicethread import ServiceThread
from utils.urlutils import UrlUtils

from controller.dispatchers.provisioningdispatcher import ProvisioningDispatcher
from controller.dispatchers.dispatcherlauncher import DispatcherLauncher

class VMManager:

    '''Class to pass the VM parameters to an RSpec Instance for ProvisioningDisaptcher'''

    @staticmethod
    def getActionInstance(servers_slivers,projectName,sliceName):
	provisioningRSpecs = list()
	action_list = list()
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
		action_list.append(actionClass.id)
                Translator.VMdictToClass(vm, actionClass.server.virtual_machines[0])
		Translator.VMdicIfacesToClass(vm['interfaces'],actionClass.server.virtual_machines[0].xen_configuration.interfaces)
                actionClass.server.uuid = server_id
                actionClass.server.virtualization_type = server.getVirtTech()
                rspec.query.provisioning.action.append(actionClass)
		provisioningRSpecs.append(rspec.query.provisioning)

	return provisioningRSpecs, action_list

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
        vm['hd-origin-path'] = "default/default.tar.gz"

	return vm
