from django.http import *
import os
import sys
from vt_manager.models import *
from vt_manager.controller import *
from vt_manager.communication.utils.XmlUtils import *
from vt_manager.utils.ServiceThread import *
from vt_manager.controller.ifaceAllocators.IPallocator import IPallocator
from vt_manager.controller.ifaceAllocators.MacAllocator import MACallocator
import xmlrpclib, time, logging

class ProvisioningResponseDispatcher():

    '''
    Handles the Agent responses when action status changes
    '''

    @staticmethod
    def processResponse(rspec):
        logging.debug("PROCESSING RESPONSE proocessResponse() STARTED...")
        for action in rspec.response.provisioning.action:
            try:
                actionModel = Action.objects.get(uuid = action.id)
            except Exception as e:
                logging.error("No action in DB with the incoming id\n%s", e)
                return

            if actionModel.status is 'QUEUED' or 'ONGOING':
                logging.debug("The incoming response has id: %s and NEW status: %s",actionModel.uuid,actionModel.status)
                
                actionModel.status = action.status
                actionModel.description = action.description
                
                #Complete information required for the Plugin: action type and VM
                action.type_ = actionModel.type
                tempVMclass = XmlHelper.getProcessingResponse('dummy', 'dummy', 'dummy').response.provisioning.action[0].virtual_machine
                tempVMclass.uuid = actionModel.vm.uuid
                action.virtual_machine = tempVMclass

                actionModel.save()
                failedOnCreate = 0 
                if actionModel.status == 'SUCCESS':
                    if actionModel.type == 'create':
                        actionModel.vm.setState('created (stopped)')
                        actionModel.vm.save()
                    elif actionModel.type == 'start' or actionModel.type == 'reboot':
                        actionModel.vm.setState('running')
                        actionModel.vm.save()
                    elif actionModel.type == 'hardStop':
                        actionModel.vm.setState('stopped')
                        actionModel.vm.save()
                    elif actionModel.type == 'delete':
                        #for mac in actionModel.vm.macs.all() :
                        #    MACallocator.release(mac)
                        #for ip in actionModel.vm.ips.all() :
                        #    IPallocator.release(ip)
                        actionModel.vm.completeDelete()
                elif actionModel.status == 'ONGOING':
                    if actionModel.type == 'create':
                        actionModel.vm.setState('creating...')
                        actionModel.vm.save()
                    elif actionModel.type == 'start':
                        actionModel.vm.setState('starting...')
                        actionModel.vm.save()
                    elif actionModel.type == 'hardStop':
                        actionModel.vm.setState('stopping...')
                        actionModel.vm.save()
                    elif actionModel.type == 'delete':
                        actionModel.vm.setState('deleting...')
                        actionModel.vm.save()
                    elif actionModel.type == 'reboot':
                        actionModel.vm.setState('rebooting...')
                        actionModel.vm.save()
                elif actionModel.status == 'FAILED':
                    if  actionModel.type == 'start':
                        actionModel.vm.setState('stopped')
                    elif actionModel.type == 'hardStop':
                        actionModel.vm.setState('running')
                    elif actionModel.type == 'reboot':
                        actionModel.vm.setState('stopped')
                    elif actionModel.type == 'create':
                        actionModel.vm.setState('failed')
                        failedOnCreate = 1
                    else:
                        actionModel.vm.setState('failed')
                    actionModel.vm.save()
                else:
                    actionModel.vm.setState('unknown')
                    actionModel.vm.save()


            else:
                try:
                    ProvisioningDispatcher.connectAndSendPlugin(actionModel.vm.getCallBackURL(), "FAILED", action.id, "Received response for an action in wrong state")
                except Exception as e:
                    logging.error("Received response for an action in wrong state\n%s",e)
                    return

            try:
                 logging.debug("Sending response to Plugin in sendAsync")
                 plugin = xmlrpclib.Server(actionModel.vm.getCallBackURL())
                 logging.debug("callBackURL = %s", actionModel.vm.getCallBackURL())
                 plugin.sendAsync(XmlHelper.craftXmlClass(rspec))
                 if failedOnCreate == 1:
                     ProvisioningDispatcher.cleanWhenFail(actionModel.vm, VTSever.objects.get(uuid = actionModel.vm.serverID))
            except Exception as e:
                logging.error("Could not connect to Plugin in sendAsync\n%s",e)
                return

