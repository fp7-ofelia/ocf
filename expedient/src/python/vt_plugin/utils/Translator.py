from vt_plugin.models import *
from vt_plugin.models.VTServer import VTServer
from vt_plugin.models.Action import Action
import copy, uuid
from datetime import datetime
from expedient.clearinghouse.aggregate.models import Aggregate
from vt_plugin.models import VTServer

class Translator():

    @staticmethod
    def VMtoModel(VMxmlClass, save = "noSave"):

       # statusTable = {
       #                 'CREATED':'created (stopped)',
       #                 'STARTED':'running',
       #                 'STOPPED':'stopped',
       #                 'ONQUEUE':'on queue',
       # }

        #search in database if VMxmlClass already exists
        if VM.objects.filter(uuid = VMxmlClass.uuid).exists():
            VMmodel = VM.objects.get(uuid=VMxmlClass.uuid)            
        else:
            VMmodel = VM()
            VMmodel.setState("on queue")
            #VMmodel.aggregate_id = VTServer.objects.get(uuid = VMxmlClass.server_id).aggregate_id

        #VMmodel.setState(statusTable.get(VMxmlClass.status))    
        VMmodel.setName(VMxmlClass.name)
        VMmodel.setUUID(VMxmlClass.uuid)
        VMmodel.setProjectId(VMxmlClass.project_id)
        VMmodel.setProjectName(VMxmlClass.project_name)
        VMmodel.setSliceId(VMxmlClass.slice_id)
        VMmodel.setSliceName(VMxmlClass.slice_name)
        VMmodel.setOStype(VMxmlClass.operating_system_type)
        VMmodel.setOSversion(VMxmlClass.operating_system_version)
        VMmodel.setOSdist(VMxmlClass.operating_system_distribution)
        VMmodel.setVirtTech(VMxmlClass.virtualization_type)
        VMmodel.setServerID(VMxmlClass.server_id)
        VMmodel.setHDsetupType(VMxmlClass.xen_configuration.hd_setup_type)
        VMmodel.setHDoriginPath(VMxmlClass.xen_configuration.hd_origin_path) 
        VMmodel.setVirtualizationSetupType(VMxmlClass.xen_configuration.virtualization_setup_type)
        VMmodel.setMemory(VMxmlClass.xen_configuration.memory_mb)
        VMmodel.aggregate_id = VTServer.objects.get(uuid = VMxmlClass.server_id).aggregate_id    
            
        #TODO: hablar con leo sobre incluir una variable disc_image para las vms...
        VMmodel.disc_image = 'Default'
        
        if save is "save":
            VMmodel.save()
        return VMmodel    

        
    @staticmethod
    def VMmodelToClass(VMmodel, VMxmlClass):

        VMxmlClass.name = VMmodel.getName()
        VMxmlClass.uuid = VMmodel.getUUID()
        VMxmlClass.project_id = VMmodel.getProjectId()
        VMxmlClass.project_name = VMmodel.getProjectName()
        VMxmlClass.slice_id = VMmodel.getSliceId()
        VMxmlClass.slice_name = VMmodel.getSliceName()
        VMxmlClass.operating_system_type = VMmodel.getOStype()
        VMxmlClass.operating_system_version = VMmodel.getOSversion()
        VMxmlClass.operating_system_distribution = VMmodel.getOSdist()
        VMxmlClass.virtualization_type = VMmodel.getVirtTech()
        VMxmlClass.server_id = VMmodel.getServerID()
        VMxmlClass.xen_configuration.hd_setup_type = VMmodel.getHDsetupType()
        VMxmlClass.xen_configuration.hd_origin_path = VMmodel.getHDoriginPath()
        VMxmlClass.xen_configuration.virtualization_setup_type = VMmodel.getVirtualizationSetupType()
        VMxmlClass.xen_configuration.memory_mb = VMmodel.getMemory()

    @staticmethod
    def ServerClassToModel(sClass, agg_id):
        #search in database if sClass already exists
        if VTServer.objects.filter(name = sClass.name).exists():
            print "sClass.name = %s" %sClass.name
            print "SERVER YA EXISTEEEEEE"
            sModel = VTServer.objects.get(name=sClass.name)
        else:
            print "sClass.name = %s" %sClass.name
            print "SERVER NO EXISTEEEEEE!!!!!"
            sModel = VTServer()
        sModel = VTServer()
        print "AFTER INSTANTIATION"
        #sModel.aggregate_id = agg_id
        sModel.name=sClass.name
        sModel.aggregate = Aggregate.objects.get(id = agg_id)
        sModel.status_change_timestamp = datetime.now()
        sModel.available = True      
        sModel.id = sClass.id
        
        
        sModel.setUUID(sClass.uuid)        
        sModel.setOStype(sClass.operating_system_type)
        sModel.setOSdist(sClass.operating_system_distribution)
        sModel.setOSversion(sClass.operating_system_version)
        sModel.setVirtTech(sClass.virtualization_type)
        sModel.setVMs()        
        sModel.save()
        print "SERVER SALVADO"
        return sModel

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
            print "TRANSLATOR SAVING..."
            actionModel.save()
        return actionModel


    @staticmethod
    def PopulateNewAction(action, vm):
        action.id = uuid.uuid4()
        action.virtual_machine.name = vm.getName()
        action.virtual_machine.uuid = vm.getUUID()
        action.virtual_machine.project_id = vm.getProjectId()
        action.virtual_machine.project_name = vm.getProjectName()
        action.virtual_machine.slice_id = vm.getSliceId()
        action.virtual_machine.slice_name = vm.getSliceName()
        action.virtual_machine.virtualization_type = vm.getVirtTech()
        action.virtual_machine.xen_configuration.hd_setup_type = vm.getHDsetupType()

    @staticmethod
    def PopulateNewVMifaces(VMclass, VMmodel):
        for iface in VMclass.xen_configuration.interfaces.interface:
            if VMmodel.ifaces.filter(name = iface.name):
                ifaceModel = VMmodel.ifaces.get(name = iface.name)
            else:
                ifaceModel = iFace()
            ifaceModel.name = iface.name
            if iface.ismgmt == True:
                ifaceModel.isMgmt = True
            else:
                ifaceModel.isMgmt = False
            ifaceModel.mac = iface.mac
            if iface.ismgmt:
                ifaceModel.ip = iface.ip
                ifaceModel.gw = iface.gw
                ifaceModel.mask = iface.mask
                ifaceModel.dns1 = iface.dns1
                ifaceModel.dns2 = iface.dns2
            ifaceModel.save()
            VMmodel.ifaces.add(ifaceModel)
            VMmodel.save()
            

