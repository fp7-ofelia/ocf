import time

import datetime
from openflow.optin_manager.sfa.util.faults import MissingSfaInfo, UnknownSfaType, \
    RecordNotFound, SfaNotImplemented, SliverDoesNotExist

from openflow.optin_manager.sfa.util.defaultdict import defaultdict
from openflow.optin_manager.sfa.util.sfatime import utcparse, datetime_to_string, datetime_to_epoch
from openflow.optin_manager.sfa.util.xrn import Xrn, hrn_to_urn, get_leaf
from openflow.optin_manager.sfa.util.cache import Cache

from openflow.optin_manager.sfa.rspecs.version_manager import VersionManager
from openflow.optin_manager.sfa.rspecs.rspec import RSpec

from openflow.optin_manager.sfa.VMAggregate import VMAggregate
from openflow.optin_manager.sfa.VTShell import VTShell

class OFSfaDriver:

	def __init__ (self, config):
		self.aggregate = OFAggregate()
		self.shell = OFShell()


	def list_resources (self,creds, options):

		version_manager = VersionManager()
        	rspec_version = version_manager.get_version(options.get('geni_rspec_version'))
        	version_string = "rspec_%s" % (rspec_version)
	        rspec =  self.aggregate.get_rspec(version=rspec_version,options=options)
       		return rspec

	def crud_slice(self,slice_leaf,authority,creds=None, action=None):

		slicename = slice_leaf 
                try:
                        slice = self.shell.GetSlice(slicename,authority)
                except Exception as e:
                        raise RecordNotFound(slice_leaf)

		if action == 'start_slice':
			self.shell.StartSlice()
		elif action == 'stop_slice':
			self.shell.StopSlice()
		elif action == 'delete_slice':
			self.shell.DeleteSlice()
		elif action == 'reset_slice':
			self.shell.RebootSlice()
		return 1

        def create_sliver (self,slice_leaf,authority,rspec_string, users, options):
		
                rspec = RSpec(rspec_string,'OcfOf')
                requested_attributes = rspec.version.get_slice_attributes()
		projectName = authority#users[0]['slice_record']['authority']
		sliceName = slice_leaf
		self.shell.CreateSliver()
		created_vms = list()
		nodes = list()
		for slivers in requested_attributes:
			node = self.shell.GetNodes()
		
		return self.aggregate.get_rspec(slice_leaf=slice_leaf,projectName=projectName,version=rspec.version)
	
	def sliver_status(self,slice_leaf,authority,creds,options):

		slice = self.shell.GetSlice(slice_leaf,authority)	
		result = dict()
		List = list()
		return result
			

		
	

