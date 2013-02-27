import copy
import uuid
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.models.VTServer import VTServer
from vt_manager.communication.sfa.vm_utils.Translator import Translator


class VMSfaManager:

    '''Class to pass the VM parameters to an RSpec Instance for ProvisioningDisaptcher'''

    @staticmethod
    def getActionInstance(servers_slivers):
	
	rspec = XmlHelper.getSimpleActionQuery()
	actionClassEmpty = copy.deepcopy(rspec.query.provisioning.action[0])
        actionClassEmpty.type_ = "create"
        rspec.query.provisioning.action.pop()
	
	
        for vms in servers_slivers:
	    server_id = vms['component_id']
	    for vm in vms['slivers']:
                print '-------------VMSfaManager-----------getActionInstance'
      	        print '------------------------------------VM:',vm
		server = VTServer.objects.get(uuid = server_id)
	        VMSfaManager.setDefaultVMParameters(vm,server)
                actionClass = copy.deepcopy(actionClassEmpty)
                actionClass.id = uuid.uuid4()
                Translator.VMdictToClass(vm, actionClass.server.virtual_machines[0])
		Translator.VMdicIfacesToClass(vm['interfaces'],actionClass.server.virtual_machines[0].xen_configuration.interfaces)
                actionClass.server.uuid = server_id
                actionClass.server.virtualization_type = server.getVirtTech()
                rspec.query.provisioning.action.append(actionClass)

	return 1   	
	#return ProvisioningDispatcher.processProvisioning(rspec.query.provisioning)	
	
    @staticmethod
    def setDefaultVMParameters(vm,server):
	
	print '-------------VMSfaManager-----------setDefaultVMParameters'
	print '------------------------------------vm',vm
	print '------------------------------------vm.keys()',vm.keys()
   
        vm['uuid'] = str(uuid.uuid4())
        #vm['serverID'] = server_id #XXX: Vms already have this parameter.
        vm['state'] = "on queue"
        vm['slice-id'] = None #TODO: check if we should use these parameters.
        vm['slice-name']= None #

        #assign same virt technology as the server where vm created
        #XXX: VirtTech can be passed with a full SFA RSpec... or should we "configure" the virtTech here?
        vm['virtualization-type'] = server.getVirtTech()
	vm['server-id'] = server.getUUID()

        #XXX: This is not necessary for SFA, I hope, probably we could assign some special IDs to save the vms
        vm['project-id'] = None
        vm['project-name'] = None
        vm['aggregate-id'] = None

        #assign parameters according to selected disc image
        #XXX: Disc Image Conf set default for now 
        #vm['disc-image'] == 'default' #XXX Where is this parameter?
        vm['operating-system-type'] = 'GNU/Linux'
        vm['operating-system-version'] = '6.0'
        vm['operating-system-distribution'] = 'Debian'
        vm['hd-origin-path'] = "default/default.tar.gz"

	return vm
 
