#from vt_manager.communication.sfa.util.version import version_core
from openflow.optin_manager.sfa.util.xrn import Xrn
from openflow.optin_manager.sfa.util.callids import Callids
from openflow.optin_manager.sfa.util.sfalogging import logger

from openflow.optin_manager.sfa.drivers.OFSfaDriver import OFSfaDriver

from openflow.optin_manager.sfa.util.faults import MissingSfaInfo, UnknownSfaType, \
    RecordNotFound, SfaNotImplemented, SliverDoesNotExist
import zlib

class AggregateManager:

    '''SFA AM Class for VM_Manager'''

    def __init__ (self, config):
	self.driver = OFSfaDriver(None)

    def GetVersion(self, api, options):
        return None

    def ListSlices(self, api, creds, options):
	raise Exception("External authorities do not have permissions to list OCF slices") 

    def ListResources(self, options):
        slice_xrn = options.get('geni_slice_urn', None)
        if slice_xrn:
            xrn = Xrn(slice_xrn,'slice')
            slice_urn = xrn.get_urn()
            slice_leaf = xrn.get_leaf()
            options['slice'] = slice_leaf
        else:
            slice_leaf = None
            slice_urn = None
        rspec = self.driver.list_resources(slice_urn,slice_leaf,options)
        if options.has_key('geni_compressed') and options['geni_compressed'] == True:
            rspec = zlib.compress(rspec).encode('base64')
        return rspec

    def SliverStatus (self, xrn, options):
        xrn = Xrn(xrn,'slice')
	slice_leaf = xrn.get_leaf()
	authority = xrn.get_authority_hrn()
	return self.driver.sliver_status(slice_leaf,authority,options)

    def CreateSliver(self, xrn, rspec_string, users,creds, options):
       #XXX: How can the expiration time be checked?
       xrn = Xrn(xrn, 'slice')
       slice_urn = xrn.get_urn()
       slice_leaf = xrn.get_leaf()
       slice_hrn = xrn.get_hrn()
       authority = xrn.get_authority_hrn()
       expiration_date =  self.driver.get_expiration_date(slice_hrn, creds)# XXX: AM may require get slice_expiration from the registry 
       return self.driver.create_sliver (slice_urn,slice_leaf,authority,rspec_string, users, options, expiration_date)

    def DeleteSliver(self, xrn, options):
        xrn = Xrn(xrn)
        slice_leaf = xrn.get_leaf()
        slice_urn = xrn.get_urn()
	authority = xrn.get_authority_hrn()
        return self.driver.crud_slice(slice_urn,authority,action='delete_slice')

    def RenewSliver(self,xrn, creds, expiration_time, options):
	#XXX: this method should extend the expiration time of the slices
	#TODO: Implement some kind of expiration date model for slices
	return True

    def start_slice(self,xrn):
        xrn = Xrn(xrn)
        slice_urn = xrn.get_urn()
	slice_leaf = xrn.get_leaf()
	authority = xrn.get_authority_hrn()
        return self.driver.crud_slice(slice_urn,authority,action='start_slice')

    def stop_slice(self,xrn):
        xrn = Xrn(xrn)
        slice_urn = xrn.get_urn()
	slice_leaf = xrn.get_leaf()
	authority = xrn.get_authority_hrn()
        return self.driver.crud_slice (slice_urn,authority,action='stop_slice')

    def reset_slice(self, xrn):
        xrn = Xrn(xrn)
	slice_leaf = xrn.get_leaf()
	authority = xrn.get_authority_hrn()
        return self.driver.crud_slice (slice_leaf,authority,action='reset_slice')

    def GetTicket(self, api, xrn, creds, rspec, users, options):
	# ticket is dead.

        raise SfaNotImplemented('Method GetTicket was deprecated.') 


