from vt_manager.models import *
import copy
import uuid

class Translator():

    @staticmethod
    def VMtoModel(VMxmlClass, callBackURL , save = "noSave"):
        VMmodel = VM()
        VMmodel.setUUID(uuid.uuid4())
        VMmodel.setCallBackURL(callBackURL)
        VMmodel.setName(VMxmlClass.name)
        VMmodel.setUUID(VMxmlClass.uuid)
        VMmodel.setProjectId(VMxmlClass.project_id)
        VMmodel.setSliceId(VMxmlClass.slice_id)
        VMmodel.setProjectName(VMxmlClass.project_name)
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
        #If the translation is doing just when the VM is created it is ok to set its state to unknow here
        VMmodel.setState("on queue")
        if save is "save":
            VMmodel.save()
        return VMmodel


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
        sClass.id = sModel.id
        sClass.uuid = sModel.getUUID()
        sClass.operating_system_type = sModel.getOStype()
        sClass.operating_system_distribution = sModel.getOSdist()
        sClass.operating_system_version = sModel.getOSversion()
        sClass.virtualization_type = sModel.getVirtTech()
        ifaces = sModel.ifaces.all()
        ifaceIndex = 0
        for iface in ifaces:
            if ifaceIndex != 0:
                newInterface = copy.deepcopy(sClass.interfaces.interface[0])
                sClass.interfaces.append(newInterface)
            sClass.interfaces.interface[ifaceIndex].name = iface.ifaceName   
            sClass.interfaces.interface[ifaceIndex].switch_id= iface.switchID   
            sClass.interfaces.interface[ifaceIndex].switch_port = iface.port  
            ifaceIndex = ifaceIndex + 1       
 
    @staticmethod
    def VMmodelToClass(VMmodel, VMxmlClass):

        #statusTable = {
        #                'created (stopped)':'CREATED',
        #                'running':'STARTED',
        #                'stopped':'STOPPED',
        #                'on queue':'ONQUEUE',
        #                'starting...':'ONQUEUE',
        #                'stopping...':'ONQUEUE',
        #                'creating...':'ONQUEUE',
        #                'deleting...':'ONQUEUE',
        #                'rebooting...':'ONQUEUE',
        #              }

        VMxmlClass.name = VMmodel.getName()
        VMxmlClass.uuid = VMmodel.getUUID()
        VMxmlClass.project_id = VMmodel.getProjectId()
        VMxmlClass.slice_id = VMmodel.getSliceId()
        VMxmlClass.project_name = VMmodel.getProjectName()
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
        #VMxmlClass.status=statusTable.get(VMmodel.state)
             
        ifaceIndex = 0
        macs = VMmodel.macs.all()
        for mac in macs:
            if(ifaceIndex != 0):
                newInterface = copy.deepcopy(VMxmlClass.xen_configuration.interfaces.interface[0])
                VMxmlClass.xen_configuration.interfaces.interface.append(newInterface)
            VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].name = mac.ifaceName
            if mac.isMgmt :
                VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].ismgmt='True'
                VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].ip = VMmodel.ips.get().ip
                VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].mask = VMmodel.ips.get().mask
                VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].gw = VMmodel.ips.get().gw
                VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].dns1 = VMmodel.ips.get().dns1
                VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].dns2 = VMmodel.ips.get().dns2
            else:
                VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].ismgmt = None
                VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].ip = None
                VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].mask = None
                VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].gw = None
                VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].dns1 = None
                VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].dns2 = None
            VMxmlClass.xen_configuration.interfaces.interface[ifaceIndex].mac = mac.mac
            ifaceIndex = ifaceIndex + 1


    @staticmethod
    def PopulateNewAction(action, vm):
        action.id = uuid.uuid4()
        action.virtual_machine.name = vm.getName()
        action.virtual_machine.uuid = vm.getUUID()
        action.virtual_machine.project_id = vm.getProjectId()
        action.virtual_machine.slice_id = vm.getSliceId()
        action.virtual_machine.project_name = vm.getProjectName()
        action.virtual_machine.slice_name = vm.getSliceName()
        action.virtual_machine.virtualization_type = vm.getVirtTech()
        action.virtual_machine.xen_configuration.hd_setup_type = vm.getHDsetupType()
                
