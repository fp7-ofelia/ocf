import time

import datetime
#
from vt_manager.communication.sfa.util.faults import MissingSfaInfo, UnknownSfaType, \
    RecordNotFound, SfaNotImplemented, SliverDoesNotExist

#from vt_manager.communication.sfa.util.sfalogging import logger
from vt_manager.communication.sfa.util.defaultdict import defaultdict
from vt_manager.communication.sfa.util.sfatime import utcparse, datetime_to_string, datetime_to_epoch
from vt_manager.communication.sfa.util.xrn import Xrn, hrn_to_urn, get_leaf
from vt_manager.communication.sfa.util.cache import Cache

# one would think the driver should not need to mess with the SFA db, but..
#from vt_manager.communication.sfa.storage.alchemy import dbsession
#from vt_manager.communication.sfa.storage.model import RegRecord

# used to be used in get_ticket
#from sfa.trust.sfaticket import SfaTicket

from vt_manager.communication.sfa.rspecs.version_manager import VersionManager
from vt_manager.communication.sfa.rspecs.rspec import RSpec

# the driver interface, mostly provides default behaviours
#from vt_manager.communication.sfa.managers.driver import Driver

from vt_manager.communication.sfa.VMAggregate import VMAggregate
from vt_manager.communication.sfa.VTShell import VTShell

class VTSfaDriver:

	def __init__ (self, config):
		self.aggregate = VMAggregate()
		self.shell = VTShell()


	def list_resources (self,creds, options):

		version_manager = VersionManager()
        	# get the rspec's return format from options
        	rspec_version = version_manager.get_version(options.get('geni_rspec_version'))
        	version_string = "rspec_%s" % (rspec_version)
	        #aggregate = VMAggregate()
	        rspec =  self.aggregate.get_rspec(version=rspec_version,options=options)
		print 'list_resources Rspec instance:',rspec
       		return rspec

	def crud_slice(self,slice_urn,slice_hrn, creds=None, action=None):
		
		#XXX: Slice_hrn: topdomain.subdomain.SliceName
		#XXX: Slice_urn: urn:publicid:IDN+topdomain:subdomain+slice+SliceName

		slicename = 'getSliceNameFromHrn'#XXX:hrn_to_dummy_slicename(slice_hrn)
                try:
                        #XXX: getSlices should return the server UUID too
                        slice = self.shell.GetSlice(slicename)
                except:
                        raise RecordNotFound(slice_hrn)
		if action == 'start_slice':
			return self.__start_slice(slice)
		elif action == 'stop_slice':
			return self.__stop_slice(slice)
		elif action == 'delete_slice':
			return self.__delete_slice(slice)
		elif action == 'reset_slice':
			return self.__reset_slice(slice)

	def __start_slice(self,slice):
        	if not slice.enabled:
            		self.shell.StartSlice(slice.server.uuid,slice.uuid)
        	return 1
	
        def __stop_slice(self,slice):
                if slice.enabled:
                        self.shell.StopSlice(slice.server.uuid,slice.uuid)
                return 1

	#XXX: this method shouldn't be private, if someone delete a slice we must "dettach" the resources asigned to this slice 
	def delete_slice(self,slice):
                self.shell.DeleteSlice(slice.server.uuid,slice.uuid)
                return 1

	def __reset_slice(self,slice):
                self.shell.RebootSlice(slice.server.uuid,slice.uuid)
                return 1

        def create_sliver (slice_urn, slice_hrn, rspec_string, users, options):
		
		#TODO: Clean input params, check if slice is already created, rspec.		

		#XXX: At the end of the day, this is only for federation, local slices are made in "OCF way"	
		#XXX: this method should parse a vm rspec, get the main attributes of the vm and send this attributes to the shell.
		#XXX: should be users? For what?
		#XXX: What about vm repeated names?	

                #XXX: what is this?--> sfa_peer = slices.get_sfa_peer(slice_hrn)

		#XXX: probably this is not necessary
                #slice_record=None
                #if users:
                #    slice_record = users[0].get('slice_record', {})

                # parse rspec

                rspec = RSpec(rspec_string)
		#XXX: if we can get the vm paramaters, we can use the shell to create a create vm action
                requested_attributes = rspec.version.get_slice_attributes()
		self.shell.CreateSliver(requested_attributes)
		
			
                # ensure slice record exists
		#XXX: Do we need this?
                #slice = slices.verify_slice(slice_hrn, slice_record, sfa_peer, options=options)
                # ensure user records exists
                #users = slices.verify_users(slice_hrn, slice, users, sfa_peer, options=options)

		#XXX: We should return something like the input rspec? 
                return aggregate.get_rspec(slice_xrn=slice_urn, version=rspec.version)

		

	
			

