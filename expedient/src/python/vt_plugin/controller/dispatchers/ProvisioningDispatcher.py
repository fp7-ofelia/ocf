from vt_manager.communication.utils.XmlUtils import *#XmlUtils
from vt_manager.communication.utils.XmlUtils import XmlHelper
import os
import sys
from vt_plugin.models import *
from vt_plugin.utils.ServiceThread import *
from vt_plugin.utils.Translator import Translator
import xmlrpclib
import threading

PLUGIN_URL = 'https://expedient:expedient@192.168.254.193:8445/xmlrpc/agent'

class ProvisioningDispatcher():
    
    '''
    manages all the (VM) provisioning actions (create, start, stop, reboot, delete)
    that go from the Vt Plugin to the VT AM
    '''
    
    @staticmethod    
    def processProvisioning(provisioning):

        print "PROVISIONING STARTED...\n"
        #go through all actions in provisioning class
        for action in provisioning.action:
            #translate action to actionModel
            actionModel = Translator.ActionToModel(action,"provisioning")
            print "ACTION = %s with id: %s" % (actionModel.type, actionModel.uuid)

            if actionModel.type == "create":
                
                if Action.objects.filter (uuid = actionModel.uuid):
                    #if action already exists we raise exception. It shouldn't exist because it is create action!
                    try:
                        raise Exception
                    except Exception as e:
                        print "Action already exists"
                        print e
                        return                
                else:
                    #we save action in local database
                    print "ACTION start is going to be saved"
                    actionModel.save()

                try:
                    #after saving action, we proceed to save the virtualmachines 
                    #(to be created) and the server modifications in local database
                    #first we translate the VM action into a VM model
                    VMmodel = Translator.VMtoModel(action.virtual_machine, "save")
                    Server = VTServer.objects.get(uuid = VMmodel.getServerID() )
                    Server.vms.add(VMmodel)
                    actionModel.vm = VMmodel
                    actionModel.save()
                except Exception as e:
                    print "Not possible to translate to VM model\n"
                    print e
                    return
                
                #finally we connect to the client server (in this case the VT AM)
                #and send the action class
                print "PROVISIONING DISPATCHER --> ACTION CREATE"
                client = Server.aggregate.as_leaf_class().client
                
                ProvisioningDispatcher.connectAndSend('https://'+client.username+':'+client.password+'@'+client.url[8:], action)                

            elif actionModel.type == "delete" :
                print "ACTION = %s with id: %s" % (actionModel.type, actionModel.uuid)

                #ProvisioningDispatcher.checkVMisPresent(action)
                VMmodel =  VM.objects.get(uuid = action.virtual_machine.uuid)
                if not  VMmodel:
                    try:
                        raise Exception
                    except Exception as e:
                        print "No VM found to start it\n"
                        print e
                        return
                    
                #ProvisioningDispatcher.checkActionIsPresent(actionModel)
                if Action.objects.filter(uuid = actionModel.uuid):
                    try:
                        raise Exception
                    except Exception as e:
                        print "Action already exists"
                        print e
                        return
                else:
                    print "ACTION delete is going to be saved"
                    actionModel.vm = VMmodel
                    actionModel.save()
                
                print "PROVISIONING DISPATCHER--> ACTION DELETE"
                Server = VTServer.objects.get(uuid = VMmodel.getServerID() )
                client = Server.aggregate.as_leaf_class().client
                ProvisioningDispatcher.connectAndSend('https://'+client.username+':'+client.password+'@'+client.url[8:], action)  

            #elif actionModel.type == "start":
            else:
                print "PROV DISPATCHER --> START, STOP, REBOOT ACTION"
                print "ACTION = %s with id: %s" % (actionModel.type, actionModel.uuid)
                
                #ProvisioningDispatcher.checkVMisPresent(action)
                VMmodel = VM.objects.get(uuid = action.virtual_machine.uuid)
                    
                if not VMmodel:
                    try:
                        raise Exception
                    except Exception as e:
                        print "No VM found to start it\n"
                        print e
                        return
                #AGENT_URL = VTServer.objects.get(name = VMmodel.getServerID() ).getAgentURL()                
                #ProvisioningDispatcher.checkActionIsPresent(actionModel)            
                if Action.objects.filter (uuid = actionModel.uuid):
                    try:
                        raise Exception
                    except Exception as e:
                        print "Action already exists"
                        print e
                        return
                else:
                    print "START, STOP, REBOOT start is going to be saved"
                    actionModel.vm = VMmodel
                    actionModel.save()
                print "PROVISIONING DISPATCHER --> START, STOP, REBOOT START"
                
                Server = VTServer.objects.get(uuid = VMmodel.getServerID() )
                client = Server.aggregate.as_leaf_class().client
                ProvisioningDispatcher.connectAndSend('https://'+client.username+':'+client.password+'@'+client.url[8:], action)                

    @staticmethod
    def connectAndSend(URL, action):
        print "PROVISIONING DISPATCHER --> CONNECTANDSEND"
        try:
            vt_manager = xmlrpclib.Server(URL)
            print "Sending ActionQuery to VT Manager\n"
            vt_manager.send("https://expedient:expedient@192.168.254.193/vt_plugin/xmlrpc/vt_am/", XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action)))
        except Exception as e:
            print "Exception connecting to VT Manager"
            print e
            return
