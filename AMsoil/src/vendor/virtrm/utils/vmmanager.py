import copy
import uuid
import threading

from resources.vtserver import VTServer
from resources.virtualmachine import VirtualMachine

from utils.xmlhelper import XmlHelper, XmlCrafter
from utils.translator import Translator
from utils.servicethread import ServiceThread
from utils.urlutils import UrlUtils

from controller.dispatchers.provisioning.query import ProvisioningDispatcher
from controller.dispatchers.launcher import DispatcherLauncher

from utils.commonbase import db_session

class VMManager:

    '''Class to pass the VM parameters to an RSpec Instance for ProvisioningDisaptcher'''

    @staticmethod
    def getActionInstance(servers_slivers,project_name,slice_name):
	provisioning_rspecs = list()
	action_list = list()
	rspec = XmlHelper.getSimpleActionQuery()
	action_class_empty = copy.deepcopy(rspec.query.provisioning.action[0])
        action_class_empty.type_ = "create"
        rspec.query.provisioning.action.pop()
        for vms in servers_slivers:
	    server_id = vms['component_id']
	    for vm in vms['slivers']:
		server = db_session.query(VTServer).filter(VTServer.uuid == server_id).first()
	        VMManager.setDefaultVMParameters(vm,server,project_name,slice_name)
		action_class = copy.deepcopy(action_class_empty)
                action_class.id = uuid.uuid4()
		action_list.append(action_class.id)
                Translator.VMdictToClass(vm, action_class.server.virtual_machines[0])
		Translator.VMdicIfacesToClass(vm['interfaces'],action_class.server.virtual_machines[0].xen_configuration.interfaces)
                action_class.server.uuid = server_id
                action_class.server.virtualization_type = server.getVirtTech()
                rspec.query.provisioning.action.append(action_class)
		provisioning_rspecs.append(rspec.query.provisioning)
    	db_session.expunge_all()
	return provisioning_rspecs, action_list

    @staticmethod
    def setDefaultVMParameters(vm,server,project_name,slice_name):
        VM = db_session.query(VirtualMachine).filter(VirtualMachine.projectName == project_name).all()
	if VM:
		vm['project-id'] = VM[0].projectId
	else:
		vm['project-id'] = str(uuid.uuid4())	

	vm['project-name'] = project_name

	vm['slice-id'] = None
	for virmach in VM:
		if virmach.slice_name == slice_name:
			vm['slice-id'] = virmach.sliceId

	if not vm['slice-id']:
		vm['slice-id'] = str(uuid.uuid4()) 

	vm['slice-name']= slice_name	 
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
	db_session.expunge_all()	
	return vm
