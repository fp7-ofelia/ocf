'''
Exposes the methods to manage resource expiration
'''

from datetime import datetime, timedelta
from controller.drivers.virt import VTDriver
from models.common.expiration import Expiration
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class ExpirationManager():
    #
    # Direct operations over Expiration
    #
    config = pm.getService("config")
    worker = pm.getService("worker")
    # Sec in the allocated state
    RESERVATION_TIMEOUT = config.get("virtrm.MAX_RESERVATION_DURATION")
    MAX_VM_DURATION = config.get("virtrm.MAX_VM_DURATION")

    EXPIRY_CHECK_INTERVAL = config.get("virtrm.EXPIRATION_VM_CHECK_INTERVAL")
    
    def __init__(self):
        # Register callback for regular updates
        self.worker.addAsReccurring("virtrm", "check_expiration_vm", None, self.EXPIRY_CHECK_INTERVAL)

#    @worker.outsideprocess
    def check_expiration_vm(self, params):
        """
        Checks expiration for both allocated and provisioned VMs
        and deletes accordingly, either from DB or disk.
        """
        return

    def check_valid_expiration_time(self, max_duration, expiration_time=None):
        """
        Check if the desired expiration time is valid
        or return the maximum expiration time if None time is given
        """
        self.max_expiration_time = datetime.now() + timedelta(0, max_duration)
        if expiration_time == None or expiration_time < datetime.now():
            return self.max_expiration_time
        elif (expiration_time > self.max_expiration_time):
            raise Exception
        else:
            return expiration_time

    def check_valid_creation_time(self, expiration_time=None):
        max_duration = self.MAX_VM_DURATION
        try:
            expiration = self.check_valid_expiration_time(max_duration, expiration_time)
        except Exception as e:
            raise e
        return expiration
        
    def check_valid_reservation_time(self, expiration_time=None):
        max_duration = self.RESERVATION_TIMEOUT
        try:
            expiration = self.check_valid_expiration_time(max_duration, expiration_time)
        except Exception as e:
            raise e
        return expiration

    def add_expiration_to_provisioned_vm(vm_uuid, expiration_time):
        pass

    def add_expiration_to_allocated_vm(vm_uuid, expiration_time):
        pass 
