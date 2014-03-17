'''
Exposes the methods to manage resource expiration
'''

from datetime import datetime, timedelta
from controller.drivers.virt import VTDriver
from models.common.expiration import Expiration, VMExpiration, VMAllocatedExpiration
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

    def is_provisioned_vm_expiration(self, expiration):
        if expiration.get_virtualmachine() and not expiration.get_virtualmachine_allocated():
            return True
        else:
            return False

    def is_allocated_vm_expiration(self, expiration):
        if expiration.get_virtualmachine_allocated() and not expiration.get_virtualmachine():
            return True
        else:
            return False

    def get_expiration_by_vm_uuid(self, vm_uuid):
        try:
            expiration_relation = VMExpiration.query.filter_by(vm_uuid=vm_uuid).one()
        except:
            expiration_relation = None
        if not expiration_relation:
            try:
                expiration_relation = VMAllocatedExpiration.query.filter_by(vm_uuid=vm_uuid).one()
            except:
                return None
        expiration = expiration_relation.get_expiration()
        return expiration

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
        expired_provisioned_vms = []
        expired_allocated_vms = []
        expirations = Expiration.query.filter(Expiration.end_time < datetime.utcnow()).all()
        for expiration in expirations:
            if self.is_allocation_vm_expiration(expiration):
                # Get the expired allocated VM
                vm = expiration.get_virtualmachine_allocated()
                expired_allocated_vms.extend(vm)
            elif self.is_provisioned_vm_expiration(expiration):
                # If the expiration is not related to an allocated VM, get the related expired provisioned VM
                vm = expiration.get_virtualmachine()
                expired_provisioned_vms.extend(vm)
            else:
                # The Expiration is not associated to any resource or both type of resources
                expiration.destroy()
        return expired_provisioned_vms, expired_allocated_vms

    def add_expiration_to_provisioned_vm_by_uuid(self, vm_uuid, expiration_time):
        #TODO: Should raise two different exceptions
        try:
            vm = VTDriver.get_vm_by_uuid(vm_uuid)
            expiration = self.check_valid_creation_time(expiration_time)
            expiration_obj = Expiration(None, expiration, True)
            expiration_obj.set_virtualmachine(vm)
        except Exception as e:
            raise e

    def add_expiration_to_allocated_vm_by_uuid(self, vm_uuid, expiration_time):
        #TODO: Should raise two different exceptions
        try:
            vm = VTDriver.get_vm_allocated_by_uuid(vm_uuid)
            expiration = self.check_valid_reservation_time(expiration_time)
            expiration_obj = Expiration(None, expiration, True)
            expiration_obj.set_virtualmachine_allocated(vm)
        except Exception as e:
            raise e

    def delete_expiration_by_vm_uuid(self, vm_uuid):
        relational_obj = VMExpiration.query.filter_by(vm_uuid=vm_uuid).first()
        if not relational_obj:
            relational_obj = VMAllocatedExpiration.query.filter_by(vm_uuid=vm_uuid).first()
        if relational_obj:
            expiration_obj = relational_obj.get_expiration()
            if not expiration_obj:
                relational_obj.destroy()
            else:
                expiration_obj.destroy()
  
    def update_expiration_by_vm_uuid(self, vm_uuid, expiration_time):
        try:
            expiration = self.check_valid_reservation_time(expiration_time)
            relational_obj = VMAllocatedExpiration.query.filter_by(vm_uuid=vm_uuid).first()
            if not relational_obj:
                relational_obj = VMExpiration.query.filter_by(vm_uuid=vm_uuid).first()
            expiration_obj = relational_obj.get_expiration()
            expiration_obj.set_do_save(True)
            expiration_obj.set_end_time(expiration)
        except Exception as e:
            raise e

