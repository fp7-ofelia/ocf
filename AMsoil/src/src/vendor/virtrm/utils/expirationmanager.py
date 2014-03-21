'''
Exposes the methods to manage resource expiration
'''

from datetime import datetime, timedelta
from controller.drivers.virt import VTDriver
from models.common.expiration import Expiration, VMExpiration
from models.resources.allocatedvm import AllocatedVM
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class ExpirationManager():
    #
    # Direct operations over Expiration
    #
    config = pm.getService("config")
    # Sec in the allocated state
    RESERVATION_TIMEOUT = config.get("virtrm.MAX_RESERVATION_DURATION")
    MAX_VM_DURATION = config.get("virtrm.MAX_VM_DURATION")

    def check_valid_expiration_time(self, max_duration, expiration_time=None):
        """
        Check if the desired expiration time is valid
        or return the maximum expiration time if None time is given
        """
        self.max_expiration_time = datetime.utcnow() + timedelta(0, max_duration)
        if expiration_time == None or expiration_time < datetime.utcnow():
            return self.max_expiration_time
        elif expiration_time > self.max_expiration_time:
            raise Exception
        else:
            return expiration_time

    def check_valid_creation_time(self, expiration_time=None):
        max_duration = self.MAX_VM_DURATION
        try:
            expiration = self.check_valid_expiration_time(max_duration, expiration_time)
            return expiration
        except Exception as e:
            raise e
        
    def check_valid_reservation_time(self, expiration_time=None):
        max_duration = self.RESERVATION_TIMEOUT
        try:
            expiration = self.check_valid_expiration_time(max_duration, expiration_time)
            return expiration
        except Exception as e:
            raise e

    def get_expiration_by_vm_uuid(self, vm_uuid):
        try
            expiration_relation = VMExpiration.query.filter_by(vm_uuid=vm_uuid).one()
        except:
            expiration_relation = None
        if expiration:
            expiration = expiration_relation.get_expiration()
            return expiration
        else:
            raise Exception

    def get_end_time_by_vm_uuid(self, vm_uuid):
        expiration = self.get_expiration_by_vm_uuid(vm_uuid)
        if expiration:
            return expiration.end_time
        else:
            return None

    def get_start_time_by_vm_uuid(self, vm_uuid):
        expiration = self.get_expiration_by_vm_uuid(vm_uuid)
        if expiration:
            return expiration.start_time
        else:
            return None

    def get_expired_vms(self):
        expired_vms = list()
        expirations = Expiration.query.filter(Expiration.end_time < datetime.utcnow()).all()
        for expiration in expirations:
            vm = expiration.get_vm()
            if vm:
                expired_vms.append(vm)
            else:
                # The Expiration is not associated to any resource
                expiration.destroy()
        return expired_vms

    def add_expiration_to_provisioned_vm_by_uuid(self, vm_uuid, expiration_time):
        #TODO: Should raise two different exceptions
        try:
            expiration = self.check_valid_creation_time(expiration_time)
        except Exception as e:
            raise e
        ExpirationManager.add_expiration_to_vm_by_uuid(self, vm_uuid, expiration)

    def add_expiration_to_allocated_vm_by_uuid(self, vm_uuid, expiration_time):
        #TODO: Should raise two different exceptions
        try:
            expiration = self.check_valid_creation_time(expiration_time)
        except Exception as e:
            raise e
        ExpirationManager.add_expiration_to_vm_by_uuid(self, vm_uuid, expiration)

    def add_expiration_to_vm_by_uuid(self, vm_uuid, expiration_time):
        try:
            vm = VTDriver.get_vm_by_uuid(vm_uuid)
            expiration_obj = Expiration(None, expiration_time, True)
            expiration_obj.set_vm(vm)
        except Exception as e:
            raise e

    def delete_expiration_by_vm_uuid(self, vm_uuid):
        try:
            relational_obj = VMExpiration.query.filter_by(vm_uuid=vm_uuid).one()
            expiration_obj = relational_obj.get_expiration()
            if not expiration_obj:
                relational_obj.destroy()
            else:
                expiration_obj.destroy()
        except Exception as e:
            raise e
  
    def update_expiration_by_vm_uuid(self, vm_uuid, expiration_time):
        try:
            relational_obj = VMExpiration.query.filter_by(vm_uuid=vm_uuid).one()
            vm = relational_obj.get_vm()
            if type(vm) is AllocatedVM:
                expiration = self.check_valid_reservation_time(expiration_time)
            else:
                expiration = self.check_valid_creation_time(expiration_time)
            expiration_obj = relational_obj.get_expiration()
            expiration_obj.set_do_save(True)
            expiration_obj.set_end_time(expiration)
        except Exception as e:
            raise e

