from controller.drivers.virt import VTDriver
from models.resources.xenserver import XenServer
from models.resources.xenvm import XenVM
from models.resources.vtserver import VTServer
from utils.httputils import HttpUtils
import threading

from utils.base import db
import amsoil.core.log

logging=amsoil.core.log.getLogger('XenDriver')

class XenDriver(VTDriver):

#    def __init__(self):
#        self.ServerClass = eval('XenServer') 
#        self.VMclass = eval('XenVM') 

    @staticmethod
    def get_instance():
        return XenDriver()

    def delete_vm(self, vm):
        try:
            vm.Server.get().delete_vm(vm)
        except:
            raise    
    
    def get_server_uuid_by_vm_id(vm_id):
        server = XenVM.query.get(vm_id).get_server()
        return server.uuid
    
    def get_server_and_create_vm(self, action, callbackurl=None):
        try:
            if not callbackurl: 
                callbackurl = threading.currentThread().callBackURL
            logging.debug("*************************** XEN PROVISIONING...")
            server = XenServer.query.filter_by(uuid=action.server.uuid).one()
            logging.debug("*************************** GOT XEN SERVER %s" % str(server))
            name, uuid, project_id, project_name, slice_id, slice_name, os_type, os_version, os_dist, memory, disc_space_gb, number_of_cpus, callback_url, hd_setup_type, hd_origin_path, virt_setup_type, save = XenDriver.xen_vm_to_model(action.server.virtual_machines[0], callbackurl, save = True)
            logging.debug("*************************** XEN VM MODEL OBTAINED...")
            try:
                logging.debug("*************************** STARTING VM CREATION WITH MODEL...")
                vm_model = server.create_vm(name,uuid,project_id,project_name,slice_id,slice_name,os_type,os_version,os_dist,memory,disc_space_gb,number_of_cpus,callback_url,hd_setup_type,hd_origin_path,virt_setup_type,save)
            except Exception as e:
                logging.debug("*************************** GO FAIL " + str(e))
                raise e
#            vm_model = Server.create_vm(XenDriver.xen_vm_to_model(action.server.virtual_machines[0],threading.currentThread().callBackURL, save = True))
            logging.debug("*************************** GO 4")
            return server, vm_model
        except Exception as e:
            raise e
    
    @staticmethod
    def create_or_update_server_from_post(request, instance):
        #return XenServer.constructor(server.getName(),server.getOSType(),server.getOSDistribution(),server.getOSVersion(),server.getAgentURL(),save=True)
        server = XenServer.query.filter_by(uuid = instance.get_uuid()).first()
        if server:
            return server.updateServer(HttpUtils.getFieldInPost(request,VTServer, "name"),
                HttpUtils.getFieldInPost(request,VTServer, "operatingSystemType"),
                HttpUtils.getFieldInPost(request,VTServer, "operatingSystemDistribution"),
                HttpUtils.getFieldInPost(request,VTServer, "operatingSystemVersion"),
                HttpUtils.getFieldInPost(request,VTServer, "agentURL"),
                save=True)
        else:
            return XenServer.constructor(HttpUtils.getFieldInPost(request,VTServer, "name"),
                                    HttpUtils.getFieldInPost(request,VTServer, "operatingSystemType"),
                                    HttpUtils.getFieldInPost(request,VTServer, "operatingSystemDistribution"),
                                    HttpUtils.getFieldInPost(request,VTServer, "operatingSystemVersion"),
                                    HttpUtils.getFieldInPost(request,VTServer, "agentURL"),
                                    save=True)
        
    def crud_server_from_instance(self,instance):
        server = XenServer.objects.filter(uuid = instance.getUUID())
        if len(server)==1:
            server = server[0]
            return server.updateServer(instance.get_name(),
                        instance.get_os_type(),
                        instance.get_os_distribution(),
                        instance.get_os_version(),
                        instance.get_agent_url(),
                        instance.get_agent_password(),
                        save = True)
        elif len(server)==0:
            return XenServer.constructor(instance.get_name(),
                                instance.get_os_type(),
                                instance.get_os_distribution(),
                                instance.get_os_version(),
                                instance.get_agent_url(),
                                instance.get_agent_password(),
                                save=True)
        else:
            raise Exception("Trying to create a server failed")
    
    @staticmethod
    def xen_vm_to_model(vm_xml_class, callback_URL, save):
        logging.debug("************************************** THIS OK 1")
        name = vm_xml_class.name
        uuid = vm_xml_class.uuid
        project_id = vm_xml_class.project_id
        project_name = vm_xml_class.project_name
        slice_id = vm_xml_class.slice_id
        slice_name = vm_xml_class.slice_name
        os_type = vm_xml_class.operating_system_type
        os_version = vm_xml_class.operating_system_version
        os_dist = vm_xml_class.operating_system_distribution
        memory = vm_xml_class.xen_configuration.memory_mb
        callback_url = callback_URL
        hd_setup_type = vm_xml_class.xen_configuration.hd_setup_type
        hd_origin_path = vm_xml_class.xen_configuration.hd_origin_path
        virt_setup_type = vm_xml_class.xen_configuration.virtualization_setup_type
        logging.debug("************************************** THIS OK 2")
        return name,uuid,project_id,project_name,slice_id,slice_name,os_type,os_version,os_dist,memory,None,None,callback_url,hd_setup_type,hd_origin_path,virt_setup_type,save
