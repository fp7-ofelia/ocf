import copy
from expedient.clearinghouse.slice.models import Slice
from expedient.clearinghouse.project.models import Project
from vt_plugin.models import VtPlugin, VTServer, VM, Action
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_plugin.utils.Translator import Translator
import xmlrpclib, uuid
from vt_plugin.utils.ServiceThread import *
from vt_plugin.controller.dispatchers.ProvisioningDispatcher import *

class VMcontroller():
    
    "manages creation of VMs from the input of a given VM formulary"
    
    @staticmethod
    def processVMCreation(instance, server_id, slice, requestUser):

        if VM.objects.filter(sliceId = slice.uuid, name =instance.name):
            raise ValidationError("Another VM with name %s already exists in this slice. Please choose a new name" % instance.name)
        rspec = XmlHelper.getSimpleActionQuery()
        actionClassEmpty = copy.deepcopy(rspec.query.provisioning.action[0])
        actionClassEmpty.type_ = "create"
        rspec.query.provisioning.action.pop()

        instance.uuid = uuid.uuid4()
        instance.serverID = server_id
        instance.state = "on queue"
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
            instance.hdOriginPath = "default/default.tar.gz"
            instance.virtualization_setup_type = "paravirtualization"
        if instance.disc_image == 'irati':
            instance.operatingSystemType = 'GNU/Linux'
            instance.operatingSystemVersion = '7.0'
            instance.operatingSystemDistribution = 'Debian'
            instance.hdOriginPath = "irati/irati.img"
            instance.virtualization_setup_type = "hvm"
        if instance.disc_image == 'spirent':
            instance.operatingSystemType = 'GNU/Linux'
            instance.operatingSystemVersion = '6.2'
            instance.operatingSystemDistribution = 'CentOS'
            instance.hdOriginPath = "spirent/spirentSTCVM.img"
            instance.virtualization_setup_type = "hvm"
        if instance.disc_image == 'debian7':
            instance.operatingSystemType = 'GNU/Linux'
            instance.operatingSystemVersion = '7.0'
            instance.operatingSystemDistribution = 'Debian'
            instance.hdOriginPath = "debian7/debian7.img"
            instance.virtualization_setup_type = "hvm"
        actionClass = copy.deepcopy(actionClassEmpty)
        actionClass.id = uuid.uuid4()
        Translator.VMmodelToClass(instance, actionClass.server.virtual_machines[0])
        server = VTServer.objects.get(uuid = server_id)
        actionClass.server.uuid = server_id
        actionClass.server.virtualization_type = server.getVirtTech()
        rspec.query.provisioning.action.append(actionClass)
         
        ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,rspec.query.provisioning, requestUser)


