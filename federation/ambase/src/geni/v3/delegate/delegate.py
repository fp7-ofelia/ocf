from ambase.src.abstract.classes.delegatebase import DelegateBase


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
                        geni_am_type=self.__config.AM_TYPE,
                        geni_am_code=self.__config.AM_CODE_VERSION,
                        geni_request_rspec_versions=reqver,
                        geni_ad_rspec_versions=adver,
                        geni_credential_types=credential_types)
        return versions
    
    def list_resources(self, geni_available=False):
        return self.__resource_manager.get_resources()
    
    def describe(self, urns=dict()):
        return self.__resource_manager.get_resources(urns)

    def reserve(self, slice_urn, reservation, expiration):
        """
        Allocate slivers
        """
        return self.__resource_manager.reserve_resources(slice_urn, reservation, expiration)
    
    def create(self, urns=list(), expiration=None):
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
        raise Exception("Unknown Operational Action %s" %str(action))
    
    def status(self, urns=list()):
        return self.__resource_manager.get_resources(urns)
        
    def renew(self, urns=list(), expiration_time=None):
        return self.__resource_manager.renew_resources(urns, expiration_time)
        
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

