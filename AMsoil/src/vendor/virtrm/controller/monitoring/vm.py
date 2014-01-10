from threading import Thread
from communication.client.xmlrpc import XmlRpcClient
from controller.actions.action import ActionController
# XXX Do something with models!
from utils.xmlhelper import XmlHelper
from utils.action import Action
from utils.urlutils import UrlUtils

'''
        author:msune
        Encapsulates VM monitoring methods        
'''

class VMMonitor(): 
    @staticmethod
    def send_update_vms(server):
        # Recover from the client the list of active VMs
        obj = XmlHelper.get_list_active_vms_query()
        # Create new Action 
        action = ActionController.create_new_action(Action.MONITORING_SERVER_VMS_TYPE, Action.QUEUED_STATUS, server.get_uuid(), "") 
        obj.query.monitoring.action[0].id = action.get_uuid() 
        obj.query.monitoring.action[0].server.virtualization_type = server.getid = server.get_virt_tech() 
        XmlRpcClient.call_method(server.get_agent_url(), "send", UrlUtils.get_own_callback_url(), 0, server.get_agent_password(), XmlHelper.craft_xml_class(obj))
        
    @staticmethod
    def process_update_vms_list(server,vm_list):
        from resources.virtualmachine import VirtualMachine
        for vm in server.get_child_object().vms.all():
            is_up = False
            for i_vm in vm_list:
                if i_vm.uuid == vm.uuid:
                    # Is running
                    vm.set_state(VirtualMachine.RUNNING_STATE)
                    is_up = True
                    break
            if is_up:
                 continue
            # Is not running
            vm.set_state(VirtualMachine.STOPPED_STATE)
        
    @staticmethod
    def process_update_vms_list_from_callback(vm_uuid,state,rspec):
        from resources.virtualmachine import VirtualMachine
        try:
            vm = VirtualMachine.query.filter_by(uuid = vm_uuid).one()
        except Exception as e:
            raise e
        if state == 'Started':
            vm.set_state(VirtualMachine.RUNNING_STATE)
        elif state == 'Stopped':
            vm.set_state(VirtualMachine.STOPPED_STATE)
        else:
            vm.set_state(VirtualMachine.UNKNOWN_STATE)
        # XXX: Maybe there better places to send to expedient this update state...        
        XmlRpcClient.call_method(vm.get_callback_url(), "sendAsync", XmlHelper.craft_xml_class(rspec))
