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
        self.max_expiration_time = datetime.utcnow() + timedelta(0, max_duration)
        if expiration_time == None or expiration_time < datetime.utcnow():
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

    def get_expiration_by_vm_uuid(self, vm_uuid):
        pass

    def get_expired_vms(self):
        expired_provisioned_vms = []
        expired_allocated_vms = []
        expirations = Expiration.query.filter(Expiration.expiration < datetime.utcnow()).all()
        for expiration in expirations:
            if expiration.is_allocation_vm_expiration():
                # Get the expired allocated VM
                vm = expiration.get_virtualmachine_allocated()
                expired_allocated_vms.extend(vm)
            elif expiration.is_provisioned_vm_expiration():
                # If the expiration is not related to an allocated VM, get the related expired provisioned VM
                vm = expiration.get_virtualmachine()
                expired_provisioned_vms.extend(vm)
            else:
                # The Expiration is not associated to any resource, remove from the database
                expiration.destroy()
        return expired_provisioned_vms, expired_allocated_vms

    def add_expiration_to_provisioned_vm(self, vm_uuid, expiration_time):
        pass

    def add_expiration_to_allocated_vm(self, vm_uuid, expiration_time):
        pass

    def remove_expiration_to_provisioned_vm(self, vm_uuid):
        pass

    def remove_expiration_to_allocated_vm(self, vm_uuid):
        pass

    def update_expiration_to_provisioned_vm(self, vm_uuid, expiration_time):
        pass

    def update_expiration_to_provisioned_vm(self, vm_uuid, expiration_time):
        pass 
