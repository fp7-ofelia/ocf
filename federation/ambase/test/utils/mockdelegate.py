from ambase.src.abstract.classes.delegatebase import DelegateBase
from ambase.src.ambase.exceptions import AllocationError
from ambase.src.ambase.exceptions import DeleteError
from ambase.src.ambase.exceptions import PerformOperationalStateError
from ambase.src.ambase.exceptions import ProvisionError
from ambase.src.ambase.exceptions import SliceAlreadyExists
from ambase.test.utils import mocksettings as config
from ambase.test.utils.mocksliver import MockSliver

class MockDelegate(DelegateBase):
    
    # TODO Mock Exceptions??
    
    def __init__(self, success_mode=True, raise_already_exists = False):
        self.success_mode = success_mode
        self.raise_already_exists = raise_already_exists
    
    def get_version(self):
        if self.success_mode:
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
        else:
            raise Exception("Mock error")
    
    def list_resources(self, geni_available=False):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock error")
    
    def describe(self, urns=dict(),credentials=dict(),options=dict()):
        if self.success_mode:
            sliver = MockSliver()
            sliver.set_slice_urn("Slice_urn")
            return [sliver]
        else:
            raise Exception("Mock error")
    
    def reserve(self, slice_urn="", am=None, expiration=None):
        if self.raise_already_exists:
            raise SliceAlreadyExists("Mock error")
        if self.success_mode:
            sliver = MockSliver()
            sliver.set_expiration(expiration)
            return [sliver]
        else:
            raise AllocationError("Mock error")
    
    def create(self, urns=list(), expiration=None):
        if self.success_mode:
            return [MockSliver()]
        else:
            raise ProvisionError("Mock error")
    
    def delete(self, urns=list()):
        if self.success_mode:
            return [MockSliver()]
        else:
            raise DeleteError("Mock error") 
    
    def perform_operational_action(self, urns=list(), action=None, geni_besteffort=True):
        if self.success_mode:
            return True
        else:
            raise PerformOperationalStateError("Mock error")
    
    def status(self, urns=list()):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock error")
    
    def renew(self, urns=list(), expiration_time=None):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock error")
    
    def shut_down(self, urns=list()):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock error")
