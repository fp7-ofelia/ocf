from controller.actions.action import ActionController
from controller.drivers.virt import VTDriver
from models.resources.resourceshash import ResourcesHash
from utils.base import db
from utils.xmlhelper import XmlHelper
import xmlrpclib, threading, logging, copy

class InformationDispatcher():
    @staticmethod
    def list_resources(remote_hash_value, project_uuid = 'None', slice_uuid ='None'):
        logging.debug("Enter listResources")
        info_rspec = XmlHelper.getSimpleInformation()
        servers = VTDriver.get_all_servers()
        base_vm = copy.deepcopy(info_rspec.response.information.resources.server[0].virtual_machine[0])
        if not servers:
            logging.debug("No VTServers available")
            info_rspec.response.information.resources.server.pop()
            resources_string = XmlHelper.craft_xml_class(info_rspec)
            local_hash_value = str(hash(resources_string))
        else:
            for s_index, server in enumerate(servers):
                if(s_index == 0):
                    base_server = copy.deepcopy(info_rspec.response.information.resources.server[0])
                if(s_index != 0):
                    new_server = copy.deepcopy(baseServer)
                    info_rspec.response.information.resources.server.append(new_server)
                InformationDispatcher.___server_model_to_class(server, info_rspec.response.information.resources.server[s_index] )
                if (project_uuid is not 'None'):
                    vms = server.get_vms(projectId = project_uuid)
                else:
                    vms = server.get_vms()
                if not vms:
                    logging.debug("No VMs available")
                    if info_rspec.response.information.resources.server[s_index].virtual_machine:
                        info_rspec.response.information.resources.server[s_index].virtual_machine.pop()
                elif (slice_uuid is not 'None'):
                    vms = vms.filter(sliceId = slice_uuid)
                    if not vms:
                        logging.error("No VMs available")
                        info_rspec.response.information.resources.server[s_index].virtual_machine.pop()
                for v_index, vm in enumerate(vms):
                    if (v_index != 0):
                        new_vm = copy.deepcopy(base_vm)
                        info_rspec.response.information.resources.server[s_index].virtual_machine.append(new_vm)
                    InformationDispatcher.__vm_model_to_class(vm, info_rspec.response.information.resources.server[s_index].virtual_machine[v_index])
            resources_string = XmlHelper.craft_xml_class(info_rspec)
            local_hash_value = str(hash(resources_string))
        try:
            r_hash_object = resourcesHash.query.filter_by(project_uuid = project_uuid).filter_by(slice_uuid = slice_uuid).one()
            r_hash_object.hash_value = local_hash_value
            db.session.add(r_hash_object)
            db.session.commit()
        except:
            r_hash_object = resourcesHash(hash_value = local_hash_value, project_uuid= project_uuid, slice_uuid = slice_uuid)
            db.session.add(r_hash_object)
            db.session.commit()
        if remoteHashValue == r_hash_object.hashValue:
            return local_hash_value, ''
        else:
            return local_hash_value, resources_string
        
    @staticmethod
    def __server_model_to_class(s_model, s_class):
        s_class.name = s_model.get_name()
        #XXX: CHECK THIS
        s_class.id = s_model.id
        s_class.uuid = s_model.get_uuid()
        s_class.operating_system_type = s_model.get_os_type()
        s_class.operating_system_distribution = s_model.get_os_distribution()
        s_class.operating_system_version = s_model.get_os_version()
        s_class.virtualization_type = s_model.get_virt_tech()
        ifaces = s_model.get_network_interfaces()
        for iface_index, iface in enumerate(ifaces):
            if iface_index != 0:
                new_interface = copy.deepcopy(s_class.interfaces.interface[0])
                s_class.interfaces.interface.append(new_interface)
            if iface.is_mgmt:
                s_class.interfaces.interface[iface_index].is_mgmt = True
            else:
                s_class.interfaces.interface[iface_index].is_mgmt = False
            s_class.interfaces.interface[iface_index].name = iface.name   
            s_class.interfaces.interface[iface_index].switch_id= iface.switch_id   
            s_class.interfaces.interface[iface_index].switch_port = iface.port  
    
    @staticmethod
    def __vm_model_to_class(vm_model, vm_xml_class):
        vm_xml_class.name = vm_model.get_name()
        vm_xml_class.uuid = vm_model.get_uuid()
        vm_xml_class.status = vm_model.get_state()
        vm_xml_class.project_id = vm_model.get_project_id()
        vm_xml_class.slice_id = vm_model.get_slice_id()
        vm_xml_class.project_name = vm_model.get_project_name()
        vm_xml_class.slice_name = vm_model.get_slice_name()
        vm_xml_class.operating_system_type = vm_model.get_os_type()
        vm_xml_class.operating_system_version = vm_model.get_os_version()
        vm_xml_class.operating_system_distribution = vm_model.get_os_distribution()
        vm_xml_class.virtualization_type = vm_model.Server.get().get_virt_tech()
        vm_xml_class.server_id = vm_model.Server.get().get_uuid()
        vm_xml_class.xen_configuration.hd_setup_type = vm_model.get_hd_setup_type()
        vm_xml_class.xen_configuration.hd_origin_path = vm_model.get_hd_origin_path()
        vm_xml_class.xen_configuration.virtualization_setup_type = vm_model.get_virtualization_setup_type()
        vm_xml_class.xen_configuration.memory_mb = vm_model.get_memory()
        ActionController.populate_networking_params(vm_xml_class.xen_configuration.interfaces.interface, vm_model)
