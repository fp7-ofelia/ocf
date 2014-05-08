'''
Exposes the methods to manage resource expiration
'''

from datetime import datetime, timedelta
from controller.drivers.virt import VTDriver
from models.common.expiration import Expiration, VMExpiration
from models.resources.virtualmachine import VirtualMachine
from utils.base import db
import utils.exceptions as virt_exception
import amsoil.core.log
import amsoil.core.pluginmanager as pm

logging=amsoil.core.log.getLogger('ExpirationManager')

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
        max_expiration_time = datetime.utcnow() + timedelta(0, max_duration)
        if expiration_time == None or expiration_time < datetime.utcnow():
            return max_expiration_time
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
        try:
            expiration_relation = VMExpiration.query.filter_by(vm_uuid=vm_uuid).one()
        except:
            expiration_relation = None
        if expiration_relation:
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
                vm_child = vm.get_child_object()
                expired_vms.append(vm_child)
            else:
                # The Expiration is not associated to any resource
                expiration.destroy()
        return expired_vms

    def add_expiration_to_vm_by_uuid(self, vm_uuid, expiration_time):
        try:
            vm = VirtualMachine.query.filter_by(uuid=vm_uuid).one()
            logging.debug("*********** VM %s EXISTS WITH NAME %s AND STATE %s" %(vm_uuid, vm.name, vm.state))
            if vm.get_state() == VirtualMachine.ALLOCATED_STATE:
                expiration = self.check_valid_reservation_time(expiration_time)
            else:
                expiration = self.check_valid_creation_time(expiration_time)
            logging.debug("********** EXPIRATION FIXED IN %s" %str(expiration))
            expiration_obj = Expiration(None, expiration, True)
            expiration_obj.set_vm(vm)
        except Exception as e:
            db.session.rollback()
            try:
                expiration_obj.destroy()
            except:
                db.session.rollback()
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
            db.session.rollback()
            raise e
  
    def update_expiration_by_vm_uuid(self, vm_uuid, expiration_time):
        try:
            if vm.get_state() == VirtualMachine.ALLOCATED_STATE:
                expiration = self.check_valid_reservation_time(expiration_time)
            else:
                expiration = self.check_valid_creation_time(expiration_time)
        except:
             raise virt_exception.VirtMaxVMDurationExceeded(expiration_time)
        try:
            relational_obj = VMExpiration.query.filter_by(vm_uuid=vm_uuid).one()
            vm = relational_obj.get_vm()
            expiration_obj = relational_obj.get_expiration()
            expiration_obj.set_do_save(True)
            expiration_obj.set_end_time(expiration)
        except Exception as e:
            logging.debug("**************** EXCEPTION TYPE => %s" % str(type(e)))
            db.session.rollback()
            raise virt_exception.VirtDatabaseError()

    def delete_expiration(self, expiration):
        try:
            expiration.destroy()
        except Exception as e:
            db.session.rollback()
            raise e
