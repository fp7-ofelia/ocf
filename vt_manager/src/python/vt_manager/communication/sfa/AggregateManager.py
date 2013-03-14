from vt_manager.communication.sfa.util.version import version_core
from vt_manager.communication.sfa.util.xrn import Xrn
from vt_manager.communication.sfa.util.callids import Callids
from vt_manager.communication.sfa.util.sfalogging import logger

from vt_manager.communication.sfa.VTSfaDriver import VTSfaDriver

from vt_manager.communication.sfa.util.faults import MissingSfaInfo, UnknownSfaType, \
    RecordNotFound, SfaNotImplemented, SliverDoesNotExist


class AggregateManager:

    ''' SFA AM Class for VM_Manager'''

    def __init__ (self, config):
	self.driver = VTSfaDriver(None)

    def GetVersion(self, api, options):
	
	#XXX: for now the version will be like this
        xrn=Xrn(api.hrn)
        version = version_core()
        version_generic = {
            'interface':'aggregate',
            'sfa': 2,
            'geni_api': 2,
            'geni_api_versions': {'2': 'http://%s:%s' % (api.config.SFA_AGGREGATE_HOST, api.config.SFA_AGGREGATE_PORT)},
            'hrn':xrn.get_hrn(),
            'urn':xrn.get_urn(),
            }
        version.update(version_generic)
        testbed_version = self.driver.aggregate_version()
        version.update(testbed_version)
        return version

    def ListSlices(self, api, creds, options):
	raise Exception("External authorities do not have permissions to list OCF slices") 

    def ListResources(self, api, creds, options):
        slice_xrn = options.get('geni_slice_urn', None)
        if slice_xrn:
	    xrn = Xrn(slice_xrn,'slice')
	    slice_leaf = xrn.get_leaf()
            options['slice'] = slice_leaf
        return self.driver.list_resources (creds, options)

    def SliverStatus (self, api, xrn, creds, options):
        xrn = Xrn(xrn,'slice')
	slice_leaf = xrn.get_leaf()
	return self.driver.sliver_status(slice_leaf,creds,options)

    def CreateSliver(self, api, xrn, creds, rspec_string, users, options):
       xrn = Xrn(xrn, 'slice')
       slice_leaf = xrn.get_leaf()
       return self.driver.create_sliver (slice_leaf,rspec_string, users, options)

    def DeleteSliver(self, api, xrn, creds, options):
	#TODO: Check the options or xrn to get a single vm.
        xrn = Xrn(xrn)
        slice_leaf = xrn.get_leaf()
        return self.driver.crud_slice(slice_leaf, creds,action='delete_slice')

    def RenewSliver(self, api, xrn, creds, expiration_time, options):
	#XXX: this method should extend the expiration time of the slices
	#TODO: Implement some kind of expiration date model for slices
	return True

    def start_slice(self, api, xrn, creds):
        xrn = Xrn(xrn)
	slice_leaf = xrn.get_leaf()
        return self.driver.crud_slice(slice_leaf, creds,action='start_slice')

    def stop_slice(self, api, xrn, creds):
        xrn = Xrn(xrn)
	slice_leaf = xrn.get_leaf()
        return self.driver.crud_slice (slice_leaf, creds,action='stop_slice')

    def reset_slice(self, api, xrn):
        xrn = Xrn(xrn)
	slice_leaf = xrn.get_leaf()
        return self.driver.crud_slice (slice_leaf,action='reset_slice')

    def GetTicket(self, api, xrn, creds, rspec, users, options):
	# ticket is dead.

        raise SfaNotImplemented('Method GetTicket was deprecated.') 


