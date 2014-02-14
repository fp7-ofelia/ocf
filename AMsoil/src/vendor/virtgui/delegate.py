#from controller.dispatchers.provisioning.query import ProvisioningDispatcher
#from controller.drivers.virt import VTDriver
#from datetime import datetime, timedelta
#from resources.vmallocated import VMAllocated
#from resources.vtserver import VTServer
#from resources.virtualmachine import VirtualMachine
#from resources.xenserver import XenServer
#from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
#from utils.action import Action
#from utils.base import db
#from utils.expires import Expires
#from utils.servicethread import ServiceThread
#from utils.vmmanager import VMManager
#from utils.xrn import *
import amsoil.core.pluginmanager as pm
import amsoil.core.log
logging=amsoil.core.log.getLogger('virtguihandler')
#import time
#import utils.exceptions as virt_exception

'''
@author: CarolinaFernandez
'''

class VirtGUI(object):
    config = pm.getService("config")
    #worker = pm.getService("virtworker")
    # FIXME or REMOVE: circular dependency
    #virtrm = pm.getService("virtrm")
    #from virtrm.controller.drivers.virt import VTDriver

    def __init__(self):
        super(VirtGUI, self).__init__()
        # Register callback for regular updates
        # FIXME: set workers back
        #self.worker.addAsReccurring("virtrm", "expire_vm", None, self.EXPIRY_CHECK_INTERVAL)
        #self.worker.addAsReccurring("virtrm", "expire_allocated_vm", None, self.EXPIRY_ALLOCATED_CHECK_INTERVAL)

    # TODO Fill...
    def serve_request(self, request):
        return "Your request is %s" % str(request)

