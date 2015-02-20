from ambase.src.abstract.classes.delegatebase import DelegateBase
from ambase.src.ambase.exceptions import SliceAlreadyExists
from ambase.src.ambase.exceptions import AllocationError
from ambase.src.ambase.exceptions import ProvisionError
from ambase.src.ambase.exceptions import DeleteError
from ambase.src.ambase.exceptions import Shutdown
from ambase.src.ambase.exceptions import PerformOperationalStateError

class GeniV3Delegate(DelegateBase):
    
    """
    Handle internal exceptions to pass to the handler
    """
    
    def __init__(self):
        self.__resource_manager = None
        self.__config = None
    
    def get_version(self):
        '''Specify version information about this AM. That could
        include API version information, RSpec format and version
        information, etc. Return a dict.'''
        reqver = [dict(type=self.__config.REQ_RSPEC_TYPE,
                       version=self.__config.REQ_RSPEC_VERSION,
                       schema=self.__config.REQ_RSPEC_SCHEMA,
                       namespace=self.__config.REQ_RSPEC_NAMESPACE,
                       extensions=self.__config.REQ_RSPEC_EXTENSIONS)]
        adver = [dict(type=self.__config.AD_RSPEC_TYPE,
                       version=self.__config.AD_RSPEC_VERSION,
                       schema=self.__config.AD_RSPEC_SCHEMA,
                       namespace=self.__config.AD_RSPEC_NAMESPACE,
                       extensions=self.__config.AD_RSPEC_EXTENSIONS)]
        
        api_versions = dict()
        api_versions[str(self.__config.GENI_API_VERSION)] = self.__config.AM_URL
        credential_types = [dict(geni_type = self.__config.CREDENTIAL_TYPE,
                                 geni_version = self.__config.GENI_API_VERSION)]
        versions = dict(geni_api= self.__config.GENI_API_VERSION,
                        geni_api_versions=api_versions,
                        geni_request_rspec_versions=reqver,
                        geni_ad_rspec_versions=adver,
                        geni_credential_types=credential_types)
        versions.keys().sort()
        extensions = self.__resource_manager.get_version()
        return versions
    
    def list_resources(self, geni_available=False):
        # No URNs are passed to this command, thus set to "None"
        return self.__resource_manager.get_resources(None, geni_available)
    
    def describe(self, urns=dict()):
        return self.__resource_manager.get_resources(urns)

    def reserve(self, slice_urn, reservation, expiration, users=list()):
        """
        Allocate slivers
        """
        try:
            return self.__resource_manager.reserve_resources(slice_urn, reservation, expiration)
        except SliceAlreadyExists as e:
            raise SliceAlreadyExists(str(e))
        except Exception as e:
            raise AllocationError(str(e))
    
    #def create(self, urns=list(), expiration=None, users=list(), geni_best_effort=True):
    # XXX Default geni_best_effort = False
    def create(self, urns=list(), expiration=None, users=list(), geni_best_effort=False):
        """
        Provision slivers
        """
        try:
            return self.__resource_manager.create_resources(urns, expiration, users)
        except Exception as e:
            raise ProvisionError(e)
    
    def delete(self, urns=list(), geni_best_effort=False):
        """
        Delete slivers
        """
        try:
            return self.__resource_manager.delete_resources(urns, geni_best_effort)
        except Exception as e:
            raise DeleteError(str(e))
    
    def perform_operational_action(self, urns=list(), action=None, geni_best_effort=False, options=dict()):
        try:
            if action == "geni_start":
                return self.__resource_manager.start_resources(urns, geni_best_effort)
            elif action == "geni_stop":
                return self.__resource_manager.stop_resources(urns, geni_best_effort)
            elif action == "geni_restart":
                return  self.__resource_manager.reboot_resources(urns, geni_best_effort)
            elif action == "geni_update_users":
                return  self.__resource_manager.update_resources_users(urns, geni_best_effort, options)
            elif action == "geni_updating_users_cancel":
                return  self.__resource_manager.cancel_update_resources_users(urns, geni_best_effort)
            elif action == "geni_console_url":
                return  self.__resource_manager.retrieve_resources_url(urns, geni_best_effort)
            raise PerformOperationalStateError("Unknown Operational Action %s" % str(action))
        except Exception as e:
            raise PerformOperationalStateError("PerformOperationalError Failed for action %s. Error was: %s " % (action, str(e)))
    
    def status(self, urns=list()):
        return self.__resource_manager.get_resources(urns)
    
    def renew(self, urns=list(), expiration_time=None, geni_best_effort=False):
        return self.__resource_manager.renew_resources(urns, expiration_time, geni_best_effort)
    
    def shut_down(self, urns=list()):
        return None
    
    def get_resource_manager(self):
        return self.__resource_manager
    
    def get_config(self):
        return self.__config
    
    def set_resource_manager(self, value):
        self.__resource_manager = value
    
    def set_config(self, value):
        self.__config = value

