from controller.actions.action import ActionController
from utils.httputils import HttpUtils
from utils.servicethread import *
from utils.xmlhelper import XmlHelper
import amsoil.core.log
import os
import sys

logging=amsoil.core.log.getLogger('VTDriver')

class VTDriver():

    CONTROLLER_TYPE_XEN = "xen"
    __possible_virt_techs = [CONTROLLER_TYPE_XEN]
    
    @staticmethod
    def get_driver(virt_type):
        from controller.drivers.xen import XenDriver
        if virt_type == VTDriver.CONTROLLER_TYPE_XEN:
            return XenDriver.get_instance()
    
    @staticmethod
    def get_all_drivers():
        from controller.drivers.xen import XenDriver
        drivers = []    
        for vt in VTDriver.__possible_virt_techs:
            drivers.append(VTDriver.get_driver(vt))
        return drivers
    
    @staticmethod
    def get_all_servers():
        from models.resources.vtserver import VTServer
        servers = VTServer.query.all()
        logging.debug("*********************************************** get_all_servers.servers: " + str(servers))
        servers_child = []
        for server in servers:
            logging.debug("***************************************** get_all_servers.server: " + str(server))
            child_server = server.get_child_object()
            logging.debug("***************************************** get_all_servers.child_server: " + str(child_server))
            servers_child.append(child_server)
        return servers_child
    
    @staticmethod
    def create_server_from_post(request, instance):
        from models.resources.vtserver import VTServer
        controller = VTDriver.get_driver(HttpUtils.getFieldInPost(request,VTServer,"virtTech"))
        return controller.create_or_update_server_from_post(request, instance)        

    @staticmethod
    def crud_server_from_instance(instance):
        # Password check. Ping is directly checked in the VTServer model
        s = xmlrpclib.Server(instance.agentURL)
        try:
            s.pingAuth("ping",instance.agentPassword)
        except:
            raise forms.ValidationError("Could not connect to server: password mismatch")
        controller = VTDriver.get_driver(instance.get_virt_tech())
        return controller.crud_server_from_instance(instance)

    @staticmethod
    def set_management_bridge(request, server):
        name = HttpUtils.getFieldInPost(request, "mgmtBridge-name")
        mac = HttpUtils.getFieldInPost(request, "mgmtBridge-mac")
        server.set_management_bridge(name, mac)

    @staticmethod
    def crud_data_bridge_from_instance(server, ifaces, ifaces_to_delete):
        server_ifaces = server.get_network_interfaces().filter_by(is_mgmt = False).all()
        for new_iface in ifaces:
            if new_iface.id == None:# or not serverIfaces.filter(id = newIface.id):
                server.add_data_bridge(new_iface.get_name(),"",new_iface.get_switch_id(),new_iface.get_port())
            else:
                server.update_data_bridge(new_iface)
        for id in ifaces_to_delete:
            if id != '':
                try:
                    server.delete_data_bridge(server_ifaces.get(id=id))
                except Exception as e:
                    raise ValidationError(str(e))

    @staticmethod
    def get_server_by_id(id):
        from models.resources.vtserver import VTServer
        try:
            return VTServer.query.get(id).get_child_object()
        except:
            raise Exception("Server does not exist or id not unique")
    
    @staticmethod
    def get_server_uuid_by_vm_id(vm_id):
        raise Exception("Server UUID is dependent on driver")
    
    @staticmethod
    def get_server_by_uuid(uuid):
        from models.resources.vtserver import VTServer
        try:
            return VTServer.query.filter_by(uuid=uuid).one().get_child_object()
        except:
            raise Exception("Server does not exist or id not unique")
    
    @staticmethod
    def get_vms_in_server(server):
        try:
            return server.vms
        except:
            raise Exception("Could not recover server VMs")

    @staticmethod
    def get_instance():
        raise Exception("Driver Class cannot be instantiated")
    
    @staticmethod    
    def get_vm_by_uuid(uuid):
        from models.resources.virtualmachine import VirtualMachine
        try:
            return VirtualMachine.query.filter_by(uuid=uuid).one().get_child_object()
        except:
            raise Exception("VM does not exist or uuid not unique")

    @staticmethod
    def get_vm_by_id(id):
        from models.resources.virtualmachine import VirtualMachine
        try:
            return VirtualMachine.query.get(id).get_child_object()
        except:
            raise Exception("Server does not exist or id not unique")

    @staticmethod
    def get_vm_allocated_by_uuid(uuid):
        from models.resources.vmallocated import VMAllocated
        try:
            return VMAllocated.query.filter_by(uuid=uuid).one()
        except:
            raise Exception("VM does not exist or uuid not unique")

    @staticmethod
    def get_vm_allocated_by_id(id):
        from models.resources.vmallocated import VMAllocated
        try:
            return VMAllocated.query.get(id)
        except:
            raise Exception("VM does not exist or id not unique")
    
    def delete_vm():
        raise Exception("Method not callable for Driver Class")
    
    def get_server_and_create_vm(): 
        raise Exception("Method not callable for Driver Class")
    
    @staticmethod
    def delete_server(server):    
        server.destroy()
    
#    @staticmethod
#    def propagateAction(vmId, serverUUID, action):
#        try:
#            from vt_manager.controller.dispatchers.ProvisioningDispatcher import ProvisioningDispatcher
#            rspec = XmlHelper.getSimpleActionSpecificQuery(action, serverUUID)
#            #MARC XXX
#            #Translator.PopulateNewAction(rspec.query.provisioning.action[0], VTDriver.get_vm_by_id(vmId))
#            ProvisioningDispatcher.process(rspec.query.provisioning)
#        except Exception as e:
#            logging.error(e)
            
    @staticmethod
    def manage_ethernet_ranges(request, server, total_mac_ranges):
        just_unsubscribed = []
        for mac_range in server.get_subscribed_mac_ranges_no_global():
            try:
                request.POST['subscribe_'+str(mac_range.id)]
            except:
                server.unsubscribe_to_mac_range(mac_range)
                just_unsubscribed.append(mac_range)
        for mac_range in total_rac_ranges:
            if mac_range not in (server.get_subscribed_mac_ranges_no_global() or just_unsubscribed):
                try:
                    request.POST['subscribe_'+str(mac_range.id)]
                    server.subscribe_ro_mac_range(mac_range)
                except:
                    pass
    
    @staticmethod
    def manage_ip4_ranges(request, server, total_ip_ranges):
        just_unsubscribed = []
        for ip_range in server.get_subscribed_ip4_ranges_no_global():
            #if not ipRange.getIsGlobal():
            try:
                request.POST['subscribe_'+str(ip_range.id)]
            except:
                server.unsubscribe_to_ip4_range(ip_range)
                just_unsubscribed.append(ip_range)
        for ip_range in total_ip_ranges:
            if ip_range not in (server.get_subscribed_ip4_ranges_no_global() or just_unsubscribed):
                try:
                    request.POST['subscribe_'+str(ip_range.id)]
                    server.subscribe_to_ip4_range(ip_range)
                except Exception as e:
                    pass
    
    @staticmethod
    def propagate_action_to_provisioning_dispatcher(vm_id, server_uuid, action):
        from models.resources.virtualmachine import VirtualMachine
        vm = VirtualMachine.query.get(vm_id).get_child_object()
        rspec = XmlHelper.get_simple_action_specific_query(action, server_uuid)
        ActionController.populate_new_action_with_vm(rspec.query.provisioning.action[0], vm)
        ServiceThread.start_method_in_new_thread(DispatcherLauncher.process_query, rspec)
