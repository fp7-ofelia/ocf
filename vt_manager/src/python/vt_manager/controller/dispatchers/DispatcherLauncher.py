from django.http import *                                                     
import os                                                                     
import sys                                                                    
from vt_manager.models import *                                               
from vt_manager.controller import *                                           
from vt_manager.controller.dispatchers.ProvisioningDispatcher import *
from vt_manager.communication.utils import *                                  
from vt_manager.utils.ServiceThread import *                                      
from vt_manager.common.rpc4django import rpcmethod                                       
from vt_manager.common.rpc4django import *                                               
import threading                                                                             

def processXmlQuery(rspec):
    
    print "[DEBUG] Processing XML query in preocessXmlQuery()"
    #check if provisioning / monitoring / etc
    if(rspec.query.provisioning != None):
        ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,rspec.query.provisioning, threading.currentThread().callBackURL)
    
    
