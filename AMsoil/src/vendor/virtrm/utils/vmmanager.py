from controller.dispatchers.launcher import DispatcherLauncher
from controller.dispatchers.provisioning.query import ProvisioningDispatcher
from resources.virtualmachine import VirtualMachine
from resources.vtserver import VTServer
from utils.base import db
from utils.servicethread import ServiceThread
from utils.translator import Translator
from utils.xmlhelper import XmlHelper, XmlCrafter
from utils.urlutils import UrlUtils
import copy
import threading
import uuid

class VMManager:
    '''Class to pass the VM parameters to an RSpec Instance for ProvisioningDisaptcher'''
    @staticmethod
    def get_action_instance(servers_slivers,project_name,slice_name):
        provisioning_rspecs = list()
        action_list = list()
        rspec = XmlHelper.get_simple_action_query()
        action_class_empty = copy.deepcopy(rspec.query.provisioning.action[0])
        action_class_empty.type_ = "create"
        rspec.query.provisioning.action.pop()
        for vms in servers_slivers:
            server_id = vms['component_id']
            for vm in vms['slivers']:
                server = VTServer.query.filter_by(uuid = server_id).one()
                VMManager.set_default_vm_parameters(vm,server,project_name,slice_name)
                action_class = copy.deepcopy(action_class_empty)
                action_class.id = uuid.uuid4()
                action_list.append(action_class.id)
                Translator.vm_dict_to_class(vm, action_class.server.virtual_machines[0])
                Translator.vm_dic_ifaces_to_class(vm['interfaces'],action_class.server.virtual_machines[0].xen_configuration.interfaces)
                action_class.server.uuid = server_id
                action_class.server.virtualization_type = server.get_virt_tech()
                rspec.query.provisioning.action.append(action_class)
                provisioning_rspecs.append(rspec.query.provisioning)
        return provisioning_rspecs, action_list

    @staticmethod
    def set_default_vm_parameters(vm,server,project_name,slice_name):
        VM = VirtualMachine.query.filter_by(project_name = project_name).all()
        if VM:
            vm['project-id'] = VM[0].project_id
        else:
            vm['project-id'] = str(uuid.uuid4())        
        vm['project-name'] = project_name
        vm['slice-id'] = None
        for virmach in VM:
            if virmach.slice_name == slice_name:
                vm['slice-id'] = virmach.slice_id
        if not vm['slice-id']:
            vm['slice-id'] = str(uuid.uuid4()) 
        vm['slice-name']= slice_name         
        vm['uuid'] = str(uuid.uuid4())
        vm['state'] = VirtualMachine.ONQUEUE_STATE
        #assign same virt technology as the server where vm created
        vm['virtualization-type'] = server.get_virt_tech()
        vm['server-id'] = server.get_uuid()
        vm['aggregate-id'] = 'aggregate-id'
        #assign parameters according to selected disc image
        vm['operating-system-type'] = 'GNU/Linux'
        vm['operating-system-version'] = '6.0'
        vm['operating-system-distribution'] = 'Debian'
        vm['hd-origin-path'] = "default/default.tar.gz"
        return vm
