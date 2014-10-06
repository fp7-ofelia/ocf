#from abc import ABCMeta
#from abc import abstractmethod

from ambase.src.abstract.classes.delegatebase import DelegateBase
from settings.src import settings as config

class GeniV3Delegate(DelegateBase):
    
    """
    Handle internal exceptions to pass to the handler
    """
    
    def __init__(self):
        self.__resource_manager = None
    
    def get_version(self):
        
        '''Specify version information about this AM. That could
        include API version information, RSpec format and version
        information, etc. Return a dict.'''
        reqver = [dict(type=config.REQ_RSPEC_TYPE,
                       version=config.REQ_RSPEC_VERSION,
                       schema=config.REQ_RSPEC_SCHEMA,
                       namespace=config.REQ_RSPEC_NAMESPACE,
                       extensions=config.REQ_RSPEC_EXTENSIONS)]
        adver = [dict(type=config.AD_RSPEC_TYPE,
                       version=config.AD_RSPEC_VERSION,
                       schema=config.AD_RSPEC_SCHEMA,
                       namespace=config.AD_RSPEC_NAMESPACE,
                       extensions=config.AD_RSPEC_EXTENSIONS)]
        api_versions = dict()
        api_versions[str(config.GENI_API_VERSION)] = config.AM_URL
        credential_types = [dict(geni_type = config.CREDENTIAL_TYPE,
                                 geni_version = config.GENI_API_VERSION)]
        versions = dict(geni_api= config.GENI_API_VERSION,
                        geni_api_versions=api_versions,
                        geni_am_type=config.AM_TYPE,
                        geni_am_code=config.AM_CODE_VERSION,
                        geni_request_rspec_versions=reqver,
                        geni_ad_rspec_versions=adver,
                        geni_credential_types=credential_types)

        return versions
    
    def list_resources(self, geni_available=False):
        
        return self.__resource_manager.get_resources()
    
    def describe(self, urns=dict()):
        return self.__resource_manager.get_resources(urns)

    def reserve(self, slice_urn, reservation,expiration):
        """
        Allocate slivers
        """

        return self.__resource_manager.reserve_resources(slice_urn, reservation, expiration)
    
    def create(self, urns=list()):
        """
        Provision slivers
        """
        return self.__resource_manager.create_resources(urns)
    
    def delete(self, urns=list()):
        """
        Delete slivers
        """
        return self.__resource_manager.delete_resources(urns)
    
    def perform_operational_action(self, urns=list(), action=None, geni_besteffort=True):
        
        if action == 'geni_start':
            return self.__resource_manager.start_resources(urns, geni_besteffort)
        elif action == 'geni_stop':
            return self.__resource_manager.stop_resources(urns, geni_besteffort)
        elif action == 'geni_restart':
            return  self.__resource_manager.reboot_resources(urns, geni_besteffort)
        raise Exception("Unknown Operational Action")
    
    def status(self, urns=list()):
        return self.__resource_manager.get_resources(urns)
        
    def renew(self, urns=list(), expiration_time=None):
        return self.__resource_manager.renew_resources(urns, expiration_time)
        
    def shut_down(self, urns=list()):
        return None

    def get_resource_manager(self):
        return self.__resource_manager

    def set_resource_manager(self, value):
        self.__resource_manager = value


