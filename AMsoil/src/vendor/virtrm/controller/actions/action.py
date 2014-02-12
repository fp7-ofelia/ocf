from models.common.action import Action
from utils.base import db
from utils.xmlhelper import XmlHelper
import uuid, copy

import amsoil.core.log
logging=amsoil.core.log.getLogger('ActionController')


class ActionController():
    @staticmethod
    def get_action(uuid):
        actions = Action.query.filter_by(uuid=uuid).all()
        print actions
        if len(actions) ==  1:
            return actions[0]
        elif len(actions) == 0:
            raise Exception("Action with uuid %s does not exist" % uuid)
        elif len(actions) > 1:
            raise Exception("More than one Action with uuid %s" % uuid)
        
    @staticmethod
    def create_new_action(a_type,status,object_uuid=None,description=""):
        return Action.constructor(a_type,status,object_uuid,description)        
    
    @staticmethod
    def complete_action_rspec(action, action_model):
        action.type_ = action_model.get_type()
        #tempVMclass = XmlHelper.getProcessingResponse('dummy', None , 'dummy').response.provisioning.action[0].server.virtual_machines[0]
        #tempVMclass.uuid = actionModel.getObjectUUID()
        #action.server.virtual_machines[0] = tempVMclass
        action.server.virtual_machines[0].uuid = action_model.get_object_uuid()
    
    #XXX: Why are these two functions here? Do not beling to the Action, aren't they?
    @staticmethod
    def populate_new_action_with_vm(action, vm):
        action.id = uuid.uuid4()
        virtual_machine = action.server.virtual_machines[0]
        virtual_machine.name = vm.get_name()
        virtual_machine.uuid = vm.get_uuid()
        virtual_machine.project_id = vm.get_project_id()
        virtual_machine.slice_id = vm.get_slice_id()
        virtual_machine.project_name = vm.get_project_name()
        virtual_machine.slice_name = vm.get_slice_name()
        virtual_machine.xen_configuration.hd_setup_type = vm.get_hd_setup_type()
    
    @staticmethod
    def populate_networking_params(action_ifaces, vm):
        from models.interfaces.networkinterface import NetworkInterface
        from sqlalchemy import desc
        logging.debug("********************************* 1")
        base_iface = copy.deepcopy(action_ifaces[0])
        logging.debug("********************************* 2")
        action_ifaces.pop()
        logging.debug("********************************* 3")
        for index, vm_iface in enumerate(vm.network_interfaces.all().order_by(NetworkInterface.is_mgmt.desc(), NetworkInterface.id)):
            logging.debug("********************************* 4 " + str(index) + ' ' + str(vm_iface))
            current_iface = copy.deepcopy(base_iface)
            logging.debug("********************************* 5")
            current_iface.ismgmt = vm_iface.is_mgmt
            logging.debug("********************************* 6")
            current_iface.name = "eth"+str(index)
            logging.debug("********************************* 7")
            current_iface.mac = vm_iface.mac.mac
            logging.debug("********************************* 8")
            # ip4s are many, but xml only accepts one
            if vm_iface.ip4s:
                logging.debug("********************************* 9 - 1")
                current_iface.ip = vm_iface.ip4s.all()[0].ip
                current_iface.mask = vm_iface.ip4s.all()[0].Ip4Range.get().netmask
                current_iface.gw = vm_iface.ip4s.all()[0].Ip4Range.get().gw
                current_iface.dns1 = vm_iface.ip4s.all()[0].Ip4Range.get().dns1
                current_iface.dns2 = vm_iface.ip4s.all()[0].Ip4Range.get().dns2
                logging.debug("********************************* 9 - 2")
                current_iface.switch_id = vm_iface.connected_to.all()[0].name
                logging.debug("********************************* 10")
                action_ifaces.append(current_iface)
                
    @staticmethod
    def action_to_model(action, hyperaction, save = "noSave" ):
        action_model = Action()
        action_model.hyperaction = hyperaction
        if not action.status:
            action_model.status = 'QUEUED'
        else:
            action_model.status = action.status
        action_model.type = action.type_
        action_model.uuid = action.id
        return action_model                                               
