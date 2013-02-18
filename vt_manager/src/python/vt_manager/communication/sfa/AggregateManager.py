from vt_manager.communication.sfa.util.version import version_core
from vt_manager.communication.sfa.util.xrn import Xrn
from vt_manager.communication.sfa.util.callids import Callids
from vt_manager.communication.sfa.util.sfalogging import logger

from vt_manager.communication.sfa.VTSfaDriver import VTSfaDriver

class AggregateManager:

    ''' SFA AM Class for VM_Manager'''

    def __init__ (self, config):
	self.driver = VTSfaDriver(None)

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
	#XXX: should this method list vms?

    def ListResources(self, api, creds, options):
        call_id = options.get('call_id')
        if Callids().already_handled(call_id): return ""
        # get slice's hrn from options
        slice_xrn = options.get('geni_slice_urn', None)
        if slice_xrn:
	    raise Exception("%s authority does not have permissions to list resources from OCF slices" %api.hrn)
		
        return self.driver.list_resources (creds, options)

    def SliverStatus (self, api, xrn, creds, options):
	#XXX: NO Sliver related things
	#XXX: Or shows the vm status? 

        #call_id = options.get('call_id')
        #if Callids().already_handled(call_id): return {}

        #xrn = Xrn(xrn,'slice')
        #slice_urn=xrn.get_urn()
        #slice_hrn=xrn.get_hrn()
        #return self.driver.sliver_status (slice_urn, slice_hrn)
	raise Exception("%s authority does not have permissions to list OCF slices" %api.hrn)

    def CreateSliver(self, api, xrn, creds, rspec_string, users, options):
       # """
       # Create the sliver[s] (slice) at this aggregate.    
       # """
       #call_id = options.get('call_id')
       #if Callids().already_handled(call_id): return ""

       #XXX:xrn = Xrn(xrn, 'slice')
       #XXX:slice_leaf = xrn.get_leaf()
       slice_leaf = None 	
       return self.driver.create_sliver (slice_leaf,rspec_string, users, options)
	#XXX: OCF VMs will be created using this method probably. All this if the Client's registry allows to pass a createSliver call
	#pass	

    def DeleteSliver(self, api, xrn, creds, options):
        #call_id = options.get('call_id')
        #if Callids().already_handled(call_id): return True

        #xrn = Xrn(xrn, 'slice')
        #slice_urn=xrn.get_urn()
        #slice_hrn=xrn.get_hrn()
        #return self.driver.delete_sliver (slice_urn, slice_hrn, creds, options)
	#XXX: If the client can create a VM using CreateSliver then the client should be able to delete it using DeleteSliver
	pass

    def RenewSliver(self, api, xrn, creds, expiration_time, options):
        #call_id = options.get('call_id')
        #if Callids().already_handled(call_id): return True

        #xrn = Xrn(xrn, 'slice')
        #slice_urn=xrn.get_urn()
        #slice_hrn=xrn.get_hrn()
        #return self.driver.renew_sliver (slice_urn, slice_hrn, creds, expiration_time, options)
	#XXX: I don't know if this method should be allowed, in the positive case,should this methoud execute a DeleteSliver + CreateSliver?
	pass

    ### these methods could use an options extension for at least call_id
    def start_slice(self, api, xrn, creds):
        xrn = Xrn(xrn)
        #slice_urn=xrn.get_urn()
        #slice_hrn=xrn.get_hrn()
	slice_leaf = xrn.get_leaf()
        return self.driver.crud_slice (slice_leaf, creds,action='start_slice')
	#XXX: Start a VM

    def stop_slice(self, api, xrn, creds):
        xrn = Xrn(xrn)
        #slice_urn=xrn.get_urn()
        #slice_hrn=xrn.get_hrn()
	slice_leaf = xrn.get_leaf()
        return self.driver.crud_slice (slice_leaf, creds,action='stop_slice')
	#XXX: Stop a VM

    def reset_slice(self, api, xrn):
	#XXX: why does not this method have creds param?
        xrn = Xrn(xrn)
        #slice_urn=xrn.get_urn()
        #slice_hrn=xrn.get_hrn()
	slice_leaf = xrn.get_leaf()
        return self.driver.crud_slice (slice_leaf,action='reset_slice')
	#XXX: Reboot vm

    def GetTicket(self, api, xrn, creds, rspec, users, options):

        #xrn = Xrn(xrn)
        #slice_urn=xrn.get_urn()
        #slice_hrn=xrn.get_hrn()

        # xxx sounds like GetTicket is dead, but if that gets resurrected we might wish
        # to pass 'users' over to the driver as well
        #return self.driver.get_ticket (slice_urn, slice_hrn, creds, rspec, options)
        pass 


