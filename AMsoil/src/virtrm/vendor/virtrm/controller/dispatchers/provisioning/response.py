from communication.client.xmlrpc import XmlRpcClient
from controller.actions.action import ActionController
from controller.drivers.virt import VTDriver
from models.common.action import Action
from models.resources.virtualmachine import VirtualMachine
from utils.base import db
from utils.xmlhelper import XmlHelper
import logging

class ProvisioningResponseDispatcher():
    """
    Handles the Agent responses when action status changes
    """   
    @staticmethod
    def process(rspec):
        """
        Process provisioning response.
        """
        logging.debug("PROCESSING RESPONSE process() STARTED...")
        actions = rspec.response.provisioning.action
        for action in actions:
            try:
                action_model = ActionController.get_action(action.id)
            except Exception as e:
                logging.error("No action in DB with the incoming uuid\n%s", e)
                return
            # If the response is for an action either in QUEUED or ONGOING status, 
            # then SUCCESS or FAILED actions are finished
            if action_model.get_status() is Action.QUEUED_STATUS or Action.ONGOING_STATUS:
                logging.debug("The incoming response has id: %s and NEW status: %s",action_model.uuid,action_model.status)
                action_model.set_status(action.status)
                action_model.set_description(action.description)
                # Complete information required for the Plugin: action type and VM
                ActionController.complete_action_rspec(action, action_model)
                # XXX: Implement this method or some other doing this job
                vm = VTDriver.get_vm_by_uuid(action_model.get_object_uuid())
                controller=VTDriver.get_driver(vm.get_server().get_virtualization_technology())
                # Update VM after obtaining a response code
                failed_on_create = False
                if action_model.get_status() == Action.SUCCESS_STATUS:
                    ProvisioningResponseDispatcher.__update_vm_after_SUCCESS(action_model, vm)
                elif action_model.get_status() == Action.ONGOING_STATUS:
                    ProvisioningResponseDispatcher.update_vm_after_ONGOING(action_model, vm)
                elif action_model.get_status() == Action.FAILED_STATUS:
                    # Return result of fail_on_create_vm
                    return ProvisioningResponseDispatcher.__update_vm_after_FAILED(action_model, vm)
                else:
                    vm.set_state(VirtualMachine.UNKNOWN_STATE)

= ProvisioningResponseDispatcher.__update_vm_after_response(action_model, vm)
                try:
                    logging.debug("Sending response to Plugin in sendAsync")
                    XmlRpcClient.callRPCMethod(vm.getCallBackURL(),"sendAsync",XmlHelper.craft_xml_class(rspec))
                    if failed_on_create:
                        controller.delete_vm(vm)
                        # Keep actions table up-to-date after each deletion
                        action_model.destroy()
                except Exception as e:
                    logging.error("Could not connect to Plugin in sendAsync\n%s",e)
                    return
            # If response is for a finished action
            else:
                try:
                    # XXX: What should be done if this happen?
                    logging.error("Received response for an action in wrong state\n")
                    XmlRpcClient.callRPCMethod(vm.get_callback_url(), "sendAsync", XmlHelper.get_processing_response(Action.ACTION_STATUS_FAILED_TYPE, action, "Received response for an action in wrong state"))
                except Exception as e:
                    logging.error(e)
                    return
        
    @staticmethod
    def __update_vm_after_SUCCESS(action_model, vm):
        if action_model.get_type() == Action.PROVISIONING_VM_CREATE_TYPE:
            vm.set_state(VirtualMachine.CREATED_STATE)
        elif action_model.get_type() is Action.PROVISIONING_VM_START_TYPE or Action.PROVISIONING_VM_REBOOT_TYPE:
            vm.set_state(VirtualMachine.RUNNING_STATE)
        elif action_model.get_type() == Action.PROVISIONING_VM_STOP_TYPE:
            vm.set_state(VirtualMachine.STOPPED_STATE)
        elif action_model.get_type() == Action.PROVISIONING_VM_DELETE_TYPE:
            controller = VTDriver.get_driver(vm.vtserver.get_virt_tech())
            controller.delete_vm(vm)
            # Keep actions table up-to-date after each deletion
            action_model.destroy()
        
    @staticmethod
    def update_vm_after_ONGOING(action_model, vm):
        if action_model.get_type() == Action.PROVISIONING_VM_CREATE_TYPE:
            vm.set_state(VirtualMachine.CREATING_STATE)
        elif action_model.get_type() == Action.PROVISIONING_VM_START_TYPE:
            vm.set_state(VirtualMachine.STARTING_STATE)
        elif action_model.get_type() == Action.PROVISIONING_VM_STOP_TYPE:
            vm.set_state(VirtualMachine.STOPPING_STATE)
        elif action_model.get_type() == Action.PROVISIONING_VM_DELETE_TYPE:
            vm.set_state(VirtualMachine.DELETING_STATE)
        elif action_model.get_type() == Action.PROVISIONING_VM_REBOOT_TYPE:
            vm.set_state(VirtualMachine.REBOOTING_STATE)
        
    @staticmethod
    def __update_vm_after_FAILED(action_model, vm):
        if  action_model.get_type() == Action.PROVISIONING_VM_START_TYPE:
            vm.set_state(VirtualMachine.STOPPED_STATE)
        elif action_model.get_type() == Action.PROVISIONING_VM_STOP_TYPE:
            vm.set_state(VirtualMachine.RUNNING_STATE)
        elif action_model.get_type() == Action.PROVISIONING_VM_REBOOT_TYPE:
            vm.set_state(VirtualMachine.STOPPED_STATE)
        elif action_model.get_type() == Action.PROVISIONING_VM_CREATE_TYPE:
            # VM deleted after sending response to the Plugin because callBackUrl is required
            # Return failed_on_create = True
            failed_on_create = True
            return failed_on_create
        else:
            vm.set_state(VirtualMachine.FAILED_STATE)
