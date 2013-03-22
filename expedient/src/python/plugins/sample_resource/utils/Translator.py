from sample_resource.models import *
from sample_resource.models.Action import Action
import copy, uuid
from datetime import datetime
from expedient.clearinghouse.aggregate.models import Aggregate
from sample_resource.models import VTServer, VTServerIface

class Translator():

    @staticmethod
    def _isInteger(x):
	try:
		y = int(x)
		return True
	except:
		return False

    @staticmethod
    def SampleResourceToModel(SampleResourceXMLClass, agg_id, save = "noSave"):
       # statusTable = {
       #                 'CREATED':'created (stopped)',
       #                 'STARTED':'running',
       #                 'STOPPED':'stopped',
       #                 'ONQUEUE':'on queue',
       # }

        #search in database if SampleResourceXMLClass already exists
        if SampleResource.objects.filter(uuid = SampleResourceXMLClass.uuid).exists():
            SampleResourceModel = SampleResource.objects.get(uuid=SampleResourceXMLClass.uuid)     
        else:
            SampleResourceModel = SampleResource()
            #lbergesio 9-1-12. Moved this line here to avoid VM's name validation after creating it and
            #maintein support of old VMs with names containing "_". 
            SampleResourceModel.setName(SampleResourceXMLClass.name)

        SampleResourceModel.setState(SampleResourceXMLClass.status)
        SampleResourceModel.setUUID(SampleResourceXMLClass.uuid)
        SampleResourceModel.setProjectId(SampleResourceXMLClass.project_id)
        SampleResourceModel.setProjectName(SampleResourceXMLClass.project_name)
        SampleResourceModel.setSliceId(SampleResourceXMLClass.slice_id)
        SampleResourceModel.setSliceName(SampleResourceXMLClass.slice_name)
        SampleResourceModel.setOStype(SampleResourceXMLClass.operating_system_type)
        SampleResourceModel.setOSversion(SampleResourceXMLClass.operating_system_version)
        SampleResourceModel.setOSdist(SampleResourceXMLClass.operating_system_distribution)
        SampleResourceModel.setVirtTech(SampleResourceXMLClass.virtualization_type)
        SampleResourceModel.setServerID(SampleResourceXMLClass.server_id)
        SampleResourceModel.setHDsetupType(SampleResourceXMLClass.xen_configuration.hd_setup_type)
        SampleResourceModel.setHDoriginPath(SampleResourceXMLClass.xen_configuration.hd_origin_path) 
        SampleResourceModel.setVirtualizationSetupType(SampleResourceXMLClass.xen_configuration.virtualization_setup_type)
        SampleResourceModel.setMemory(SampleResourceXMLClass.xen_configuration.memory_mb)
        SampleResourceModel.aggregate_id = agg_id    
        #SampleResourceModel.aggregate_id = VTServer.objects.get(uuid = SampleResourceXMLClass.server_id).aggregate_id    
        #TODO: hablar con leo sobre incluir una variable disc_image para las vms...
        SampleResourceModel.disc_image = 'Default'
        
        if save is "save":
            SampleResourceModel.save()
        return SampleResourceModel    

        
    @staticmethod
    def SampleResourceModelToClass(SampleResourceModel, SampleResourceXMLClass):
        try:
            SampleResourceXMLClass.name = SampleResourceModel.getName()
            SampleResourceXMLClass.uuid = SampleResourceModel.getUUID()
            SampleResourceXMLClass.status = SampleResourceModel.getState()
            SampleResourceXMLClass.project_id = SampleResourceModel.getProjectId()
            SampleResourceXMLClass.project_name = SampleResourceModel.getProjectName()
            SampleResourceXMLClass.slice_id = SampleResourceModel.getSliceId()
            SampleResourceXMLClass.slice_name = SampleResourceModel.getSliceName()
            SampleResourceXMLClass.operating_system_type = SampleResourceModel.getOStype()
            SampleResourceXMLClass.operating_system_version = SampleResourceModel.getOSversion()
            SampleResourceXMLClass.operating_system_distribution = SampleResourceModel.getOSdist()
            SampleResourceXMLClass.virtualization_type = SampleResourceModel.getVirtTech()
            SampleResourceXMLClass.server_id = SampleResourceModel.getServerID()
            SampleResourceXMLClass.xen_configuration.hd_setup_type = SampleResourceModel.getHDsetupType()
            SampleResourceXMLClass.xen_configuration.hd_origin_path = SampleResourceModel.getHDoriginPath()
            SampleResourceXMLClass.xen_configuration.virtualization_setup_type = SampleResourceModel.getVirtualizationSetupType()
            SampleResourceXMLClass.xen_configuration.memory_mb = SampleResourceModel.getMemory()
        except Exception as e:
			print e
			return
#    @staticmethod
#    def ServerClassToModel(sClass, agg_id):
#        #print "[[[Translating Server XML description into plugin dataModel]]]"
#       	sModel = None 
#        if VTServer.objects.filter(uuid = sClass.uuid).exists():
#            sModel = VTServer.objects.get(uuid=sClass.uuid)
#        else:
#            sModel = VTServer()
#       
#        try:
#            #sModel.aggregate_id = agg_id
#            sModel.name=sClass.name
#            sModel.aggregate = Aggregate.objects.get(id = agg_id)
#            sModel.status_change_timestamp = datetime.now()
#            sModel.available = True      
#            sModel.setUUID(sClass.uuid)        
#            sModel.setOStype(sClass.operating_system_type)
#            sModel.setOSdist(sClass.operating_system_distribution)
#            sModel.setOSversion(sClass.operating_system_version)
#            sModel.setVirtTech(sClass.virtualization_type)
#            #for iface in sClass.interfaces.interface:
#            #VTServer instance needs to be saved in order to be able to create many-to-many relationships
#            #for the interfaces and VMs
#            sModel.save()
#            for iface in sClass.interfaces.interface:
#                ifaceModel = None
#                if iface.ismgmt:
#                    sModel.setVmMgmtIface(iface.name) #XXX: remove, no longer used
#                if sModel.ifaces.filter(ifaceName = iface.name):
#		    ifaceModel = sModel.ifaces.get(ifaceName = iface.name)
#		else:
#		    ifaceModel = VTServerIface()
#		ifaceModel.ifaceName = iface.name
#		ifaceModel.switchID = iface.switch_id
#		ifaceModel.isMgmt = iface.ismgmt 
#    		 
#                if Translator._isInteger(iface.switch_port):
#                    ifaceModel.port = iface.switch_port
#                ifaceModel.save()
#                if not sModel.ifaces.filter(ifaceName = iface.name):
#                    sModel.ifaces.add(ifaceModel)
#            sModel.setVMs()        
#            sModel.save()
#            return sModel
#        except Exception as e:
#            print e
#            print "Error tranlating Server Class to Model"

    @staticmethod
    def ActionToModel(action, hyperaction, save = "noSave"):#, callBackUrl):
        actionModel = Action()
        actionModel.hyperaction = hyperaction
        if not action.status:
            actionModel.status = 'QUEUED'
        else:
            actionModel.status = action.status
        #actionModel.callBackUrl = callBackUrl


        actionModel.type = action.type_

        actionModel.uuid = action.id
        if save is "save":
            actionModel.save()
        return actionModel


    @staticmethod
    def PopulateNewAction(action, vm):
        action.id = uuid.uuid4()
		
        virtual_machine = action.server.virtual_machines[0]
        virtual_machine.name = vm.getName()
        virtual_machine.uuid = vm.getUUID()
        virtual_machine.project_id = vm.getProjectId()
        virtual_machine.project_name = vm.getProjectName()
        virtual_machine.slice_id = vm.getSliceId()
        virtual_machine.slice_name = vm.getSliceName()
        virtual_machine.virtualization_type = vm.getVirtTech()
        virtual_machine.xen_configuration.hd_setup_type = vm.getHDsetupType()

    @staticmethod
    def PopulateNewVMifaces(SampleResourceClass, SampleResourceModel):
        for iface in SampleResourceClass.xen_configuration.interfaces.interface:
            if SampleResourceModel.ifaces.filter(name = iface.name):
                ifaceModel = SampleResourceModel.ifaces.get(name = iface.name)
            else:
                ifaceModel = iFace()
            ifaceModel.name = iface.name
            if iface.ismgmt == True:
                ifaceModel.isMgmt = True
            else:
                ifaceModel.isMgmt = False
            ifaceModel.mac = iface.mac
            ifaceModel.bridgeIface = iface.switch_id
            if iface.ismgmt:
                ifaceModel.ip = iface.ip
                ifaceModel.gw = iface.gw
                ifaceModel.mask = iface.mask
                ifaceModel.dns1 = iface.dns1
                ifaceModel.dns2 = iface.dns2
            ifaceModel.save()
            SampleResourceModel.ifaces.add(ifaceModel)
            SampleResourceModel.save()
            

