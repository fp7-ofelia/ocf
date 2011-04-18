from vt_manager.communication.utils.XmlUtils import *#XmlUtils
from vt_manager.communication.utils.XmlUtils import XmlHelper
import os
import sys
from vt_manager.models import *
from vt_manager.models.Ip import Ip
from vt_manager.controller import *
from vt_manager.controller.ifaceAllocators.MacAllocator import MACallocator
from vt_manager.controller.ifaceAllocators.IPallocator import IPallocator
from vt_manager.controller.policy.PolicyManager import PolicyManager
from vt_manager.communication.utils import *
from vt_manager.utils.ServiceThread import *
from vt_manager.controller.utils.Translator import Translator
import xmlrpclib, threading, logging, copy
from vt_manager.settings import ROOT_USERNAME, ROOT_PASSWORD, VTAM_URL

class ProvisioningDispatcher():
    @staticmethod
    
    def processProvisioning(provisioning):

        logging.debug("PROVISIONING STARTED...\n")
        for action in provisioning.action:
            actionModel = Translator.ActionToModel(action,"provisioning")
            logging.debug("ACTION type: %s with id: %s" % (actionModel.type, actionModel.uuid))
    
            '''
            PROVISIONING CREATE
            '''
            if actionModel.type == "create":
                
                if Action.objects.filter(uuid = actionModel.uuid):
                    try:
                        ProvisioningDispatcher.connectAndSendPlugin(threading.currentThread().callBackURL, "FAILED", action.id, "Action already exists in VT AM")
                        raise Exception
                    except Exception as e:
                        logging.error("Action already exists\n")
                        logging.error(e)
                        return
                
                #elif not PolicyManager.checkPolicies(action):
                if not PolicyManager.checkPolicies(action):
                    try:
                        ProvisioningDispatcher.connectAndSendPlugin(threading.currentThread().callBackURL, "FAILED", action.id, "Action does not pass Policies")
                        raise Exception
                    except Exception as e:
                        logging.error("The requested action do not pass the Aggregate Manager Policies")
                        logging.error(e)
                        return
                else:
                    actionModel.save()

                try:
                    VMmodel = Translator.VMtoModel(action.virtual_machine, threading.currentThread().callBackURL, save="save" )
                    Server = VTServer.objects.get(uuid = VMmodel.getServerID() )
                    Server.vms.add(VMmodel)
                    actionModel.vm = VMmodel
                    actionModel.save()
                except Exception as e:
                    ProvisioningDispatcher.connectAndSendPlugin(threading.currentThread().callBackURL, "FAILED", action.id, "Not possible to create VM")
                    logging.error("Not possible to translate to VM model\n")
                    logging.error(e)
                    return
                
                try:
                    ProvisioningDispatcher.setVMinterfaces(VMmodel, action.virtual_machine)
                except Exception as e:
                    ProvisioningDispatcher.connectAndSendPlugin(threading.currentThread().callBackURL, "FAILED", action.id, "Could not set VM interfaces")
                    logging.error("Not possible to set VM interfaces\n")
                    logging.error(e)
                    return
 
                ProvisioningDispatcher.connectAndSendAgent(Server.agentURL, action)
                
            
            ### PROVISIONING DELETE ###
          

            elif actionModel.type == "delete" :

                VMmodel =  VM.objects.get(uuid = action.virtual_machine.uuid)
                if not  VMmodel:
                    try:
                        raise Exception
                    except Exception as e:
                        logging.error("No VM found to start it\n")
                        logging.error(e)
                        return
                
                AGENT_URL = VTServer.objects.get(uuid = VMmodel.getServerID() ).getAgentURL()
                PLUGIN_URL = VMmodel.getCallBackURL()

                if Action.objects.filter(uuid = actionModel.uuid):
                    try:
                        ProvisioningDispatcher.connectAndSendPlugin( PLUGIN_URL, "FAILED", action.id, "Action with the same id already exists")
                        raise Exception
                    except Exception as e:
                        logging.error("Action already exists")
                        logging.error(e)
                        return

                elif not PolicyManager.checkPolicies(action):
                    try:
                        ProvisioningDispatcher.connectAndSendPlugin( PLUGIN_URL, "FAILED", action.id, "Action does not pass Policies")
                        raise Exception
                    except Exception as e:
                        logging.error("The requested action do not pass the Aggregate Manager Policies")
                        logging.error(e)
                        return
                else:
                    actionModel.vm = VMmodel
                    actionModel.save()

                
                #VMmodel = VM.objects.get(uuid = action.virtual_machine.uuid)

                ProvisioningDispatcher.connectAndSendAgent(AGENT_URL, action)

            else: 
                
                VMmodel = VM.objects.get(uuid = action.virtual_machine.uuid)
                    
                if not VMmodel:
                    try:
                        raise Exception
                    except Exception as e:
                        print "[EXCEPTION] No VM found to start it\n"
                        print e
                        return
                
                AGENT_URL = VTServer.objects.get(uuid = VMmodel.getServerID() ).getAgentURL()
                PLUGIN_URL = VMmodel.getCallBackURL()

                if Action.objects.filter(uuid = actionModel.uuid):
                    try:
                        ProvisioningDispatcher.connectAndSendPlugin( PLUGIN_URL, "FAILED", action.id, "Action already exists")
                        raise Exception
                    except Exception as e:
                        print "[EXCEPTION] Action already exists"
                        print e
                        return

                elif not PolicyManager.checkPolicies(action):
                    try:
                        ProvisioningDispatcher.connectAndSendPlugin( PLUGIN_URL, "FAILED", action.id, "Action does not pass Policies")
                        raise Exception
                    except Exception as e:
                        print "[EXCEPTION] The requested action do not pass the Aggregate Manager Policies"
                        print e
                        return
                else:
                    actionModel.vm = VMmodel
                    actionModel.save()
            
                ProvisioningDispatcher.connectAndSendAgent(AGENT_URL, action)

        print "[DEBUG] PROVISIONING FINISHED..."

    #        if action.type_ == "modify" :
    #            #Send async notification
    #            XmlRpcClient.sendAsyncProvisioningActionStatus(action.id,"ONGOING","")
    #            dispatcher.modifyVM(action.id,vm)
    #        if action.type_ == "delete" :
    #            #Send async notification
    #            XmlRpcClient.sendAsyncProvisioningActionStatus(action.id,"ONGOING","")
    #            dispatcher.deleteVM(action.id,vm)


    @staticmethod
    def setVMinterfaces(VMmodel, VMxmlClass):
        #Data interfaces
        for i, ServerIface in enumerate(VTServer.objects.get(uuid = VMmodel.getServerID()).ifaces.all()):
            if i != 0:
                newInterface = copy.deepcopy(VMxmlClass.xen_configuration.interfaces.interface[0])
                VMxmlClass.xen_configuration.interfaces.interface.append(newInterface)
            else:
                newInterface = VMxmlClass.xen_configuration.interfaces.interface[0]
            newInterface.ismgmt = False
            newInterface.name = 'eth'+str(i+1)
            newInterface.mac = MACallocator.acquire(VMxmlClass.project_id, 1, VMxmlClass.slice_id, VMxmlClass.uuid, newInterface.name)
            newInterface.switch_id = ServerIface.ifaceName
        #Mgmt Interface
        newInterface = copy.deepcopy(VMxmlClass.xen_configuration.interfaces.interface[0])
        VMxmlClass.xen_configuration.interfaces.interface.append(newInterface)
        newInterface.ismgmt = True
        newInterface.name = 'eth0'
        newInterface.mac = MACallocator.acquire(VMxmlClass.project_id, 1, VMxmlClass.slice_id, VMxmlClass.uuid, newInterface.name, True)
        newInterface.switch_id = VTServer.objects.get(uuid = VMmodel.getServerID()).getVmMgmtIface()
        iptemp = IPallocator.acquire(VMxmlClass.server_id, VMxmlClass.project_id, 1, VMxmlClass.slice_id, VMxmlClass.uuid, newInterface.name, True)
        newInterface.ip = iptemp.ip
        newInterface.mask = iptemp.mask
        newInterface.gw = iptemp.gw
        newInterface.dns1 = iptemp.dns1
        newInterface.dns2 = iptemp.dns2
        #Relate the IPs created with the VMmodel
        try:
            VMmodel.setIPs()
        except Exception as e:
            print e
            raise e

        VMmodel.setMacs()

    @staticmethod
    def checkVMisPresent(action):
        
        if not  VM.objects.get(uuid = action.virtual_machine.uuid):
            try:
                raise Exception
            except Exception as e:
                print "No VM found to start it\n"
                print e
                return

    @staticmethod
    def checkActionIsPresent(actionModel):
        if Action.objects.filter (uuid = actionModel.uuid):
            try:
                raise Exception
            except Exception as e:
                #raise e
                print "Action already exists"
                print e
                return
        else:
            print "ACTION start is going to be saved"
            actionModel.save()

    @staticmethod
    def connectAndSendAgent(AGENT_URL, action):
        try:
            agent = xmlrpclib.Server(AGENT_URL)
            print "[DEBUG] Sending ActionQuery to Agent in https://"+ROOT_USERNAME+":"+ROOT_PASSWORD+"@"+VTAM_URL
            print "XMLTOPLUGIN"
            print XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action))
            agent.send("https://"+ROOT_USERNAME+":"+ROOT_PASSWORD+"@"+VTAM_URL,1, "hfw9023jf0sdjr0fgrbjk",XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action)))
        except Exception as e:
            print "[EXCEPTION] Exception connecting to Agent"
            print e
            return

    @staticmethod
    def connectAndSendPlugin(url, status,id, description):
        try:
            plugin = xmlrpclib.Server(url)
            print "[DEBUG] Sending ONGOING/FAILED response to Plugin\n"
            plugin.sendAsync(XmlHelper.craftXmlClass(XmlHelper.getProcessingResponse(status,id, description)))
        except Exception as e:
            print "[EXCEPTION] Exception connecting to Plugin"
            print e
            return

