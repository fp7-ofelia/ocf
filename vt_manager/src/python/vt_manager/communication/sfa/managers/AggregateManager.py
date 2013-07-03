from vt_manager.communication.sfa.util.version import version_core
from vt_manager.communication.sfa.util.xrn import Xrn
from vt_manager.communication.sfa.util.callids import Callids

from vt_manager.communication.sfa.drivers.VTSfaDriver import VTSfaDriver

from vt_manager.communication.sfa.util.faults import MissingSfaInfo, UnknownSfaType, \
    RecordNotFound, SfaNotImplemented, SliverDoesNotExist


class AggregateManager:

    ''' SFA AM Class for VM_Manager'''

    def __init__ (self, config=None):
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

    def ListResources(self, options):
        slice_xrn = options.get('geni_slice_urn', None)
        if slice_xrn:
            xrn = Xrn(slice_xrn,'slice')
            slice_leaf = xrn.get_leaf()
            options['slice'] = slice_leaf
        rspec = self.driver.list_resources(options)
        if options.has_key('geni_compressed') and options['geni_compressed'] == True:
            rspec = zlib.compress(rspec).encode('base64')
        return rspec

    def SliverStatus (self, xrn, options):
        xrn = Xrn(xrn,'slice')
	slice_leaf = xrn.get_leaf()
	authority = xrn.get_authority_hrn()
	return self.driver.sliver_status(slice_leaf,authority,options)

    def CreateSliver(self, xrn, rspec_string, users, options):
        xrn = Xrn(xrn, 'slice')
        slice_leaf = xrn.get_leaf()
        authority = xrn.get_authority_hrn()
        return self.driver.create_sliver (slice_leaf,authority,rspec_string, users, options)

    def DeleteSliver(self, xrn, options):
	#TODO: Check the options or xrn to get a single vm.
        xrn = Xrn(xrn)
        slice_leaf = xrn.get_leaf()
	authority = xrn.get_authority_hrn()
        return self.driver.crud_slice(slice_leaf,authority,action='delete_slice')

    def RenewSliver(self, xrn, expiration_time, options):
	return True

    def start_slice(self,xrn):
        xrn = Xrn(xrn)
	slice_leaf = xrn.get_leaf()
	authority = xrn.get_authority_hrn()
        return self.driver.crud_slice(slice_leaf,authority,action='start_slice')

    def stop_slice(self,xrn):
        xrn = Xrn(xrn)
	slice_leaf = xrn.get_leaf()
	authority = xrn.get_authority_hrn()
        return self.driver.crud_slice (slice_leaf,authority,action='stop_slice')

    def reset_slice(self,xrn):
        xrn = Xrn(xrn)
	slice_leaf = xrn.get_leaf()
	authority = xrn.get_authority_hrn()
        return self.driver.crud_slice (slice_leaf,authority,action='reset_slice')

    def GetTicket(self, api, xrn, creds, rspec, users, options):
	# ticket is dead.

        raise SfaNotImplemented('Method GetTicket was deprecated.') 


