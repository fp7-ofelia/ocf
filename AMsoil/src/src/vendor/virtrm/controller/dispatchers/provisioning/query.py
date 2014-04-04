from communication.client.xmlrpc import XmlRpcClient
from controller.actions.action import ActionController
from controller.drivers.virt import VTDriver
from controller.policies.ruletablemanager import RuleTableManager
from models.common.action import Action
from utils.base import db
from utils.urlutils import UrlUtils
from utils.xmlhelper import XmlHelper
import amsoil.core.log
import xmlrpclib, threading, copy

logging=amsoil.core.log.getLogger('ProvisioningDispatcher')

class ProvisioningDispatcher():        
    @staticmethod
    def process(provisioning, callback_url=None):
        """
        Process provisioning query.
        """
        # Assign the callBackURL this way so this method can be called without a ServiceThread
        if not callback_url:
            callback_url = threading.currentThread().callBackURL
        logging.debug("PROVISIONING STARTED...\n")
        for action in provisioning.action:
            action_model = ActionController.action_to_model(action, "provisioning")
            logging.debug("ACTION type: %s with id: %s" % (action_model.type, action_model.uuid))
            try:
                logging.debug("************************** 1")
                RuleTableManager.Evaluate(action,RuleTableManager.getDefaultName())
                logging.debug("************************** 2")
            except Exception as e:
                logging.debug("************************** 3" + str(e))
                a = str(e)
                if len(a)>200:
                    a = a[0:199]
                XmlRpcClient.call_method(callback_url, "sendAsync", XmlHelper.craft_xml_class(XmlHelper.get_processing_response(Action.FAILED_STATUS, action, a)))
#                XmlRpcClient.call_method(threading.currentThread().callBackURL, "sendAsync", XmlHelper.craft_xml_class(XmlHelper.get_processing_response(Action.FAILED_STATUS, action, a)))
                return None
            try:
                controller = VTDriver.get_driver(action.server.virtualization_type)
                # XXX:Change this when xml schema is updated
                server = VTDriver.get_server_by_uuid(action.server.uuid)
                #if actionModel.getType() == Action.PROVISIONING_VM_CREATE_TYPE:
                #    server = VTDriver.get_server_by_uuid(action.virtual_machine.server_id)
                #else:
                #    server = VTDriver.get_vm_by_uuid(action.virtual_machine.uuid).Server.get()
            except Exception as e:
                logging.error(e)
                raise e
            try:        
                logging.debug("******************************* A")
                # PROVISIONING CREATE
                if action_model.get_type() == Action.PROVISIONING_VM_CREATE_TYPE:
                    try:
                        logging.debug("*********************************** B")
                        vm = ProvisioningDispatcher.__create_vm(controller, actionModel, action)
                    except:
                        vm = None
                        raise
                # PROVISIONING DELETE, START, STOP, REBOOT
                else :
                    logging.debug("***************************** C")
                    ProvisioningDispatcher.__delete_start_stop_reboot_vm(controller, action_model, action)
                    logging.debug("********************************* D")
                    XmlRpcClient.call_method(server.get_agent_url(), "send", UrlUtils.getOwnCallbackURL(), 1, server.get_agent_password(),XmlHelper.craft_xml_class(XmlHelper.get_simple_action_query(action)))
                    logging.debug("********************************* E")
            except Exception as e:
                logging.debug("********************************* ERROR " + str(e) + ' ' +  str(server))
                if action_model.get_type() == Action.PROVISIONING_VM_CREATE_TYPE:
                    # If the VM creation was interrupted in the network
                    # configuration, the created VM won't be returned
                    try:
                        if not vm:
                            vm = controller.get_vm_by_uuid(action.server.virtual_machines[0].uuid)
                        controller.delete_vm(vm)
                    except Exception as e:
                        print "Could not delete VM. Exception: %s" % str(e)
                        XmlRpcClient.call_method(callback_url, "sendAsync", XmlHelper.craft_xml_class(XmlHelper.get_processing_response(Action.FAILED_STATUS, action, str(e))))
#                        XmlRpcClient.call_method(threading.currentThread().callBackURL, "sendAsync", XmlHelper.craft_xml_class(XmlHelper.get_processing_response(Action.FAILED_STATUS, action, str(e))))
        logging.debug("PROVISIONING FINISHED...")
        
    @staticmethod
    def __create_vm(controller, action_model, action):
        try:
            logging.debug("**************************** OK - 1")
            action_model.check_action_is_present_and_unique()
            logging.debug("**************************** OK - 2")
            Server, VMmodel = controller.get_server_and_create_vm(action)
            logging.debug("**************************** OK - 3")
            ActionController.populate_networking_params(action.server.virtual_machines[0].xen_configuration.interfaces.interface, VMmodel)
            logging.debug("**************************** OK - 4")
            # XXX: change action Model
            action_model.set_object_uuid(VMmodel.get_uuid())
            logging.debug("**************************** OK - 5")
            db.session.add(action_model)
            db.session.commit()
            return VMmodel
        except:
            raise
    
    @staticmethod
    def __delete_start_stop_reboot_vm(controller, action_model, action):
        try:
            action_model.check_action_is_present_and_unique()
            VMmodel =  controller.get_vm_by_uuid(action.server.virtual_machines[0].uuid)
            if not VMmodel:
                logging.error("VM with uuid %s not found\n" % action.server.virtual_machines[0].uuid)
                raise Exception("VM with uuid %s not found\n" % action.server.virtual_machines[0].uuid)
            # XXX: change action Model
            action_model.set_object_uuid(VMmodel.get_uuid())
            db.session.add(action_model)
            db.session.commit()
        except:
            raise 
