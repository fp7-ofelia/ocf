
import amsoil.core.pluginmanager as pm

GENIv3DelegateBase = pm.getService('geniv3delegatebase')
geni_ex = pm.getService('geniv3exceptions')
dhcp_ex = pm.getService('dummyexceptions')

class DummyDelegate(GENIv3DelegateBase):
    """
	A Dummy Delegate for testing
    """

    def __init__(self):
        super(DummyDelegate, self).__init__()
        self._resource_manager = pm.getService("dummyresourcemanager")
    
    def get_request_extensions_mapping(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return {'dummy' : 'http://example.com/dummy'} # /request.xsd

    def get_manifest_extensions_mapping(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return {'dummy' : 'http://example.com/dummy'} # /manifest.xsd

    def get_ad_extensions_mapping(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return {'dummy' : 'http://example.com/dummy'} # /ad.xsd

    def is_single_allocation(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return False

    def get_allocation_mode(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return 'geni_many'


    def list_resources(self, client_cert, credentials, geni_available):
	"""Documentation see [geniv3rpc] GENIv3DelegateBase."""
	#check if the certificate and credentials are correct for this method
	#self.auth(client_cert, credentials, None, ('listslices',))

	#call our specific RM and get anything we need. Do whatever you need with these values
	value1 = self._resource_manager.do_something()
        value2 = self._resource_manager.do_something_else()

	#get the values into geniv3 format
	root_node = self.lxml_ad_root()
        E = self.lxml_ad_element_maker('dummy')
        r = E.resource()
	r.append(E.first(value1))
	r.append(E.second(value2))
	root_node.append(r)

	return self.lxml_to_string(root_node)
 
    def describe(self, urns, client_cert, credentials):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return "Dummy delegate working! Describe"

    def allocate(self, slice_urn, client_cert, credentials, rspec, end_time=None):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
	return "Dummy delegate working! Allocate"

    def renew(self, urns, client_cert, credentials, expiration_time, best_effort):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
	return "Dummy delegate working! Renew"   
 
    def provision(self, urns, client_cert, credentials, best_effort, end_time, geni_users):
        """Documentation see [geniv3rpc] GENIv3DelegateBase.
        {geni_users} is not relevant here."""
        return "Dummy delegate working! Provision"

    def status(self, urns, client_cert, credentials):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
	return "Dummy delegate working! Status"

    def delete(self, urns, client_cert, credentials, best_effort):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return "Dummy delegate working! Delete"
    
    def shutdown(self, slice_urn, client_cert, credentials):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return "Dummy delegate working! Shutdown"
