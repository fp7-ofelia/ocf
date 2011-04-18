import copy
from expedient.clearinghouse.slice.models import Slice
from expedient.clearinghouse.project.models import Project
from vt_plugin.models import VtPlugin, VTServer, VM, Action
from vt_manager.communication.utils.XmlUtils import XmlHelper
from vt_plugin.utils.Translator import Translator
import xmlrpclib, uuid
from vt_plugin.utils.ServiceThread import *
from vt_plugin.controller.dispatchers.ProvisioningDispatcher import *

class VMcontroller():
    
    "manages creation of VMs from the input of a given VM formulary"
    
    @staticmethod
    def processVMCreation(instances, server_id, slice, requestUser):
        
        rspec = XmlHelper.getSimpleActionQuery()
        actionClassEmpty = copy.deepcopy(rspec.query.provisioning.action[0])
        actionClassEmpty.type_ = "create"
        rspec.query.provisioning.action.pop()
        for instance in instances:
            instance.uuid = uuid.uuid4()
            instance.serverID = server_id
            instance.sliceId = slice.uuid
            instance.sliceName= slice.name

            #assign same virt technology as the server where vm created
            s = VTServer.objects.get(uuid = server_id)
            instance.virtTech = s.virtTech
            instance.projectId = slice.project.uuid
            instance.projectName = slice.project.name
	    instance.aggregate_id = s.aggregate_id
            #assign parameters according to selected disc image
            #TODO get the rest of image choices! 
            if instance.disc_image == 'test':
                instance.operatingSystemType = 'GNU/Linux'
                instance.operatingSystemVersion = '6.0'
                instance.operatingSystemDistribution = 'Debian'
		instance.hdOriginPath = "default/test/lenny"
	    if instance.disc_image == 'default':
                instance.operatingSystemType = 'GNU/Linux'
                instance.operatingSystemVersion = '6.0'
                instance.operatingSystemDistribution = 'Debian'
		instance.hdOriginPath = "default/squeeze"

            actionClass = copy.deepcopy(actionClassEmpty)
            actionClass.id = uuid.uuid4()
            Translator.VMmodelToClass(instance, actionClass.virtual_machine)
            rspec.query.provisioning.action.append(actionClass)
        
        ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,rspec.query.provisioning, requestUser)
