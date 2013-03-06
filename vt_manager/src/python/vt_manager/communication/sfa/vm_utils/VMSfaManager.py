import copy
import uuid
import threading

from vt_manager.communication.utils.XmlHelper import XmlHelper, XmlCrafter
from vt_manager.models.VTServer import VTServer
from vt_manager.communication.sfa.vm_utils.Translator import Translator

from vt_manager.utils.ServiceThread import ServiceThread
from vt_manager.utils.UrlUtils import UrlUtils

from vt_manager.controller.dispatchers.xmlrpc.ProvisioningDispatcher import ProvisioningDispatcher
from vt_manager.controller.dispatchers.xmlrpc.DispatcherLauncher import DispatcherLauncher

class VMSfaManager:

    '''Class to pass the VM parameters to an RSpec Instance for ProvisioningDisaptcher'''

    @staticmethod
    def getActionInstance(servers_slivers):
	provisioningRSpecs = list()
	rspec = XmlHelper.getSimpleActionQuery()
	actionClassEmpty = copy.deepcopy(rspec.query.provisioning.action[0])
        actionClassEmpty.type_ = "create"
        rspec.query.provisioning.action.pop()
        for vms in servers_slivers:
	    server_id = vms['component_id']
	    for vm in vms['slivers']:
		server = VTServer.objects.get(uuid = server_id)
	        VMSfaManager.setDefaultVMParameters(vm,server)
		actionClass = copy.deepcopy(actionClassEmpty)
                actionClass.id = uuid.uuid4()
                Translator.VMdictToClass(vm, actionClass.server.virtual_machines[0])
		Translator.VMdicIfacesToClass(vm['interfaces'],actionClass.server.virtual_machines[0].xen_configuration.interfaces)
                actionClass.server.uuid = server_id
                actionClass.server.virtualization_type = server.getVirtTech()
                rspec.query.provisioning.action.append(actionClass)
		provisioningRSpecs.append(rspec.query.provisioning)

		print XmlCrafter.craftXML(rspec.query.provisioning)			
	return provisioningRSpecs
		#return ProvisioningDispatcher.processProvisioning(rspec.query.provisioning)	
	
    @staticmethod
    def setDefaultVMParameters(vm,server):
   
        vm['uuid'] = str(uuid.uuid4())
        #vm['serverID'] = server_id #XXX: Vms already have this parameter.
        vm['state'] = "on queue"
        vm['slice-id'] = 'slice-id' #TODO: check if we should use these parameters.
        vm['slice-name']= 'slice-name' #

        #assign same virt technology as the server where vm created
        #XXX: VirtTech can be passed with a full SFA RSpec... or should we "configure" the virtTech here?
        vm['virtualization-type'] = server.getVirtTech()
	vm['server-id'] = server.getUUID()

        #XXX: This is not necessary for SFA, I hope, probably we could assign some special IDs to save the vms
        vm['project-id'] = 'project-id'
        vm['project-name'] = 'project-name'
        vm['aggregate-id'] = 'aggregate-id'

        #assign parameters according to selected disc image
        #XXX: Disc Image Conf set default for now 
        #vm['disc-image'] == 'default' #XXX Where is this parameter?
        vm['operating-system-type'] = 'GNU/Linux'
        vm['operating-system-version'] = '6.0'
        vm['operating-system-distribution'] = 'Debian'
        vm['hd-origin-path'] = "default/default.tar.gz"

	return vm
 
