import os
import sys

from utils.servicethread import *
from utils.xmlhelper import XmlHelper
from utils.httputils import HttpUtils
from resources.virtualmachine import VirtualMachine
from controller.actions.action import ActionController

from utils.commonbase import db_session
import amsoil.core.log
#amsoil logger
logging=amsoil.core.log.getLogger('VTDriver')

class VTDriver():

    CONTROLLER_TYPE_XEN = "xen"
    __possibleVirtTechs = [CONTROLLER_TYPE_XEN]


    @staticmethod
    def get_driver(virtType):
        from controller.drivers.xen import XenDriver
        if virtType == VTDriver.CONTROLLER_TYPE_XEN:
            return XenDriver.get_instance()

    @staticmethod
    def get_all_drivers():
        from controller.drivers.xen import XenDriver
        drivers = []    
        for vt in VTDriver.__possibleVirtTechs:
            drivers.append(VTDriver.get_driver(vt))
        return drivers

    @staticmethod
    def get_all_servers():
        from resources.vtserver import VTServer
        servers = db_session.query(VTServer).all()
        logging.debug("***********************************************" + str(servers))
        serversChild = []
        for server in servers:
            logging.debug("*****************************************" + str(server))
            child_server = server.getChildObject()
            logging.debug("*****************************************" + str(child_server))
            serversChild.append(child_server)
        return serversChild

    
    @staticmethod
    def create_server_from_post(request, instance):
        from resources.vtserver import VTServer
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
        controller = VTDriver.get_driver(instance.getVirtTech())
        return controller.crud_server_from_instance(instance)

    @staticmethod
    def set_management_bridge(request, server):
        name = HttpUtils.getFieldInPost(request, "mgmtBridge-name")
        mac = HttpUtils.getFieldInPost(request, "mgmtBridge-mac")
        server.set_management_bridge(name, mac)

    @staticmethod
    def crud_data_bridge_from_instance(server,ifaces, ifacesToDelete):
        serverIfaces = server.getNetworkInterfaces().filter(isMgmt = False)
        for newIface in ifaces:
            if newIface.id == None:# or not serverIfaces.filter(id = newIface.id):
                server.addDataBridge(newIface.getName(),"",newIface.getSwitchID(),newIface.getPort())
            else:
                server.updateDataBridge(newIface)
        for id in ifacesToDelete:
            if id != '':
                try:
                    server.deleteDataBridge(serverIfaces.get(id=id))
                except Exception as e:
                    raise ValidationError(str(e))

    @staticmethod
    def get_server_by_id(id):
        from resources.vtserver import VTServer
        try:
            return db_session.query(VTServer).filter(VTServer.id==id).first().getChildObject()
        except:
            raise Exception("Server does not exist or id not unique")
    
    @staticmethod
    def get_server_by_uuid(uuid):
        from resources.vtserver import VTServer
        try:
            return db_session.query(VTServer).filter(VTServer.uuid == uuid).one().getChildObject()
        except:
            raise Exception("Server does not exist or id not unique")

    @staticmethod
    def get_vms_in_server(server):
        from resources.vtserver import VTServer
        try:
            return server.vms
        except:
            raise Exception("Could not recover server VMs")

    @staticmethod
    def get_instance():
        raise Exception("Driver Class cannot be instantiated")
    
    @staticmethod    
    def get_vm_by_uuid(uuid):
        try:
            return db_session.query(VirtualMachine).filter(VirtualMachine.uuid==uuid).one().getChildObject()
        except:
            raise Exception("VM does not exist or uuid not unique")

    @staticmethod
    def get_vm_by_id(id):
        try:
            return db_session.query(VirtualMachine).filter(VirtualMachine.id==id).one().getChildObject()
        except:
            raise Exception("Server does not exist or id not unique")

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
    def manage_ethernet_ranges(request, server, totalMacRanges):
        justUnsubscribed = []
        for macRange in server.getSubscribedMacRangesNoGlobal():
            try:
                request.POST['subscribe_'+str(macRange.id)]
            except:
                server.unsubscribeToMacRange(macRange)
                justUnsubscribed.append(macRange)
        for macRange in totalMacRanges:
            if macRange not in (server.getSubscribedMacRangesNoGlobal() or justUnsubscribed):
                try:
                    request.POST['subscribe_'+str(macRange.id)]
                    server.subscribeToMacRange(macRange)
                except:
                    pass

    @staticmethod
    def manage_ip4_ranges(request, server, totalIpRanges):
        justUnsubscribed = []
        for ipRange in server.getSubscribedIp4RangesNoGlobal():
            #if not ipRange.getIsGlobal():
            try:
                request.POST['subscribe_'+str(ipRange.id)]
            except:
                server.unsubscribeToIp4Range(ipRange)
                justUnsubscribed.append(ipRange)

        for ipRange in totalIpRanges:
            if ipRange not in (server.getSubscribedIp4RangesNoGlobal() or justUnsubscribed):
                try:
                    request.POST['subscribe_'+str(ipRange.id)]
                    server.subscribeToIp4Range(ipRange)
                except Exception as e:
                    pass

    @staticmethod
    def propagate_action_to_provisioning_dispatcher(vm_id, serverUUID, action):
        vm = db_session.query(VirtualMachine).filter(VirtualMachine.id==vm_id).getChildObject()
        rspec = XmlHelper.getSimpleActionSpecificQuery(action, serverUUID)
        ActionController.PopulateNewActionWithVM(rspec.query.provisioning.action[0], vm)
        ServiceThread.startMethodInNewThread(DispatcherLauncher.process_query, rspec)
