from sfa.util.version import version_core
from sfa.util.xrn import Xrn
from sfa.util.callids import Callids
from sfa.util.sfalogging import logger

from VTSfaDriver import VTSfaDriver

class AggregateManager:

    ''' SFA AM Class for VM_Manager'''

    def __init__ (self, config): pass

    # essentially a union of the core version, the generic version (this code) and
    # whatever the driver needs to expose
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
        #call_id = options.get('call_id')
        #if Callids().already_handled(call_id): return []
        #return self.driver.list_slices (creds, options)

	#XXX:This method shoud raise an exeption, these AM methods will only be executed by federated SMs.

	#TODO: SFAException??
	raise Exception("%s authority does not have permissions to list OCF slices" %api.hrn) 
	

    def ListResources(self, api, creds, options):
        call_id = options.get('call_id')
        if Callids().already_handled(call_id): return ""
        # get slice's hrn from options
        slice_xrn = options.get('geni_slice_urn', None)
        if slice_xrn:
	    raise Exception("%s authority does not have permissions to list resources from OCF slices" %api.hrn)
	
        return VTSfaDriver.list_resources (creds, options)

    def SliverStatus (self, api, xrn, creds, options):
        call_id = options.get('call_id')
        if Callids().already_handled(call_id): return {}

        xrn = Xrn(xrn,'slice')
        slice_urn=xrn.get_urn()
        slice_hrn=xrn.get_hrn()
        return self.driver.sliver_status (slice_urn, slice_hrn)

    def CreateSliver(self, api, xrn, creds, rspec_string, users, options):
        """
        Create the sliver[s] (slice) at this aggregate.    
        Verify HRN and initialize the slice record in PLC if necessary.
        """
        call_id = options.get('call_id')
        if Callids().already_handled(call_id): return ""

        xrn = Xrn(xrn, 'slice')
        slice_urn=xrn.get_urn()
        slice_hrn=xrn.get_hrn()

        return self.driver.create_sliver (slice_urn, slice_hrn, creds, rspec_string, users, options)

    def DeleteSliver(self, api, xrn, creds, options):
        call_id = options.get('call_id')
        if Callids().already_handled(call_id): return True

        xrn = Xrn(xrn, 'slice')
        slice_urn=xrn.get_urn()
        slice_hrn=xrn.get_hrn()
        return self.driver.delete_sliver (slice_urn, slice_hrn, creds, options)

    def RenewSliver(self, api, xrn, creds, expiration_time, options):
        call_id = options.get('call_id')
        if Callids().already_handled(call_id): return True

        xrn = Xrn(xrn, 'slice')
        slice_urn=xrn.get_urn()
        slice_hrn=xrn.get_hrn()
        return self.driver.renew_sliver (slice_urn, slice_hrn, creds, expiration_time, options)

    ### these methods could use an options extension for at least call_id
    def start_slice(self, api, xrn, creds):
        xrn = Xrn(xrn)
        slice_urn=xrn.get_urn()
        slice_hrn=xrn.get_hrn()
        return self.driver.start_slice (slice_urn, slice_hrn, creds)

    def stop_slice(self, api, xrn, creds):
        xrn = Xrn(xrn)
        slice_urn=xrn.get_urn()
        slice_hrn=xrn.get_hrn()
        return self.driver.stop_slice (slice_urn, slice_hrn, creds)

    def reset_slice(self, api, xrn):
        xrn = Xrn(xrn)
        slice_urn=xrn.get_urn()
        slice_hrn=xrn.get_hrn()
        return self.driver.reset_slice (slice_urn, slice_hrn)

    def GetTicket(self, api, xrn, creds, rspec, users, options):

        xrn = Xrn(xrn)
        slice_urn=xrn.get_urn()
        slice_hrn=xrn.get_hrn()

        # xxx sounds like GetTicket is dead, but if that gets resurrected we might wish
        # to pass 'users' over to the driver as well
        return self.driver.get_ticket (slice_urn, slice_hrn, creds, rspec, options)

                                                                                                                                            117,0-1       Bot

