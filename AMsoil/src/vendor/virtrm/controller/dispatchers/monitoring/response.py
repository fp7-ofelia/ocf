from models.common.action import Action
from utils.xmlhelper import XmlHelper
import logging

class MonitoringResponseDispatcher():
    """
    Handles the Agent responses when action status changes
    """
    @staticmethod
    def process(rspec):
        logging.debug("-------------------> Monitoring!!!!!")
        for action in rspec.response.monitoring.action:
            logging.debug(action)
            if not action.type_ == "listActiveVMs":
                raise Exception("Cannot process Monitoring action:"+action.type_)
            try:
                if action.id == "callback":
                    logging.debug('---------------------->Libvirt Monitoring!!!')
                    from controller.monitoring.vm import VMMonitor
                    from models.resources.vtserver import VTServer
                    print '------>UUID',action.server.virtual_machines[0].uuid
                    logging.debug('------>STATUS',action.server.virtual_machines[0].status)
                    VMMonitor.process_update_vms_list_from_callback(action.server.virtual_machines[0].uuid, action.server.virtual_machines[0].status, rspec)
                    logging.debug('---------------------->LibvirtMonitoring Finished!!!')
                    return
                else:
                    action_model = Action.get_and_check_action_by_uuid(action.id)
            except Exception as e:
                logging.error("No action in DB with the incoming uuid\n%s", e)
                return
            if action.status == "ONGOING":
                logging.debug("----------------------->ONGOING")
                # ONGOING
                action_model.set_status(Action.ONGOING_STATUS)
                return
            elif action.status == "SUCCESS":
                from models.resources.vtserver import VTServer
                from controller.monitoring.vm import VMMonitor
                logging.debug("----------------------->SUCCESS")
                server = VTServer.query.filter_by(uuid=action_model.get_object_uuid())
                logging.debug("----------------------->SUCCESS2")
                VMMonitor.process_update_vms_list(server,action.server.virtual_machines)        
                action_model.destroy()
            elif action.status == "FAILED":
                logging.debug("----------------------->FAILED!!")
                action_model.set_status(Action.FAILED_STATUS)        
