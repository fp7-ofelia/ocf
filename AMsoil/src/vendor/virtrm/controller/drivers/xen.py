from controller.drivers.virt import VTDriver
from resources.xenserver import XenServer
from resources.xenvm import XenVM
from resources.vtserver import VTServer
from utils.httputils import HttpUtils
import threading

from utils.commonbase import db_session
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

    def get_server_and_create_vm(self,action):
        try: 
            logging.debug("*************************** GO 1")
            server = db_session.query(XenServer).filter(XenServer.uuid == action.server.uuid).one()
            logging.debug("*************************** GO 2" + str(server))
            name, uuid, project_id, project_name, slice_id, slice_name, os_type, os_version, os_dist, memory, discSpaceGB, numberOfCPUs, callback_url, hd_setup_type, hd_origin_path, virt_setup_type, save = XenDriver.xen_vm_to_model(action.server.virtual_machines[0],threading.currentThread().callback_URL, save = True)
            logging.debug("*************************** GO 3")
            try:
                vm_model = server.create_vm(name,uuid,project_id,project_name,slice_id,slice_name,os_type,os_version,os_dist,memory,discSpaceGB,numberOfCPUs,callback_url,hd_setup_type,hd_origin_path,virt_setup_type,save)
            except Exception as e:
                logging.debug("*************************** GO FAIL " + str(e))
#            vm_model = Server.create_vm(XenDriver.xen_vm_to_model(action.server.virtual_machines[0],threading.currentThread().callBackURL, save = True))
            logging.debug("*************************** GO 4")
            return server, vm_model
        except:
            raise
    
    @staticmethod
    def create_or_update_server_from_post(request, instance):
        #return XenServer.constructor(server.getName(),server.getOSType(),server.getOSDistribution(),server.getOSVersion(),server.getAgentURL(),save=True)
        server = XenServer.objects.get(uuid = instance.getUUID())
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
            return server.updateServer(instance.getName(),
                        instance.getOSType(),
                        instance.getOSDistribution(),
                        instance.getOSVersion(),
                        instance.getAgentURL(),
                        instance.getAgentPassword(),
                        save = True)
        elif len(server)==0:
            return XenServer.constructor(instance.getName(),
                                instance.getOSType(),
                                instance.getOSDistribution(),
                                instance.getOSVersion(),
                                instance.getAgentURL(),
                                instance.getAgentPassword(),
                                save=True)
        else:
            raise Exception("Trying to create a server failed")

    @staticmethod
    def xen_vm_to_model(VMxmlClass, callback_URL, save):
        logging.debug("************************************** THIS OK 1")
        name = VMxmlClass.name
        uuid = VMxmlClass.uuid
        project_id = VMxmlClass.project_id
        project_name = VMxmlClass.project_name
        slice_id = VMxmlClass.slice_id
        slice_name = VMxmlClass.slice_name
        os_type = VMxmlClass.operating_system_type
        os_version = VMxmlClass.operating_system_version
        os_dist = VMxmlClass.operating_system_distribution
        memory = VMxmlClass.xen_configuration.memory_mb
        callback_url = callback_URL
        hd_setup_type = VMxmlClass.xen_configuration.hd_setup_type
        hd_origin_path = VMxmlClass.xen_configuration.hd_origin_path
        virt_setup_type = VMxmlClass.xen_configuration.virtualization_setup_type
        logging.debug("************************************** THIS OK 2")
        return name,uuid,project_id,project_name,slice_id,slice_name,os_type,os_version,os_dist,memory,None,None,callback_url,hd_setup_type,hd_origin_path,virt_setup_type,save
