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

		for vm in slice['vms']:
			if action == 'start_slice':
				self.shell.StartSlice(vm['node-id'],vm['vm-id'])
			elif action == 'stop_slice':
				self.shell.StopSlice(vm['node-id'],vm['vm-id'])
			elif action == 'delete_slice':
				self.shell.DeleteSlice(vm['node-id'],vm['vm-id'])
			elif action == 'reset_slice':
				self.shell.RebootSlice(vm['node-id'],vm['vm-id'])
		return 1

        def create_sliver (self,slice_leaf,authority,rspec_string, users, options):
		
                rspec = RSpec(rspec_string,'OcfVt')
                requested_attributes = rspec.version.get_slice_attributes()
		projectName = authority#users[0]['slice_record']['authority']
		sliceName = slice_leaf	
		self.shell.CreateSliver(requested_attributes,projectName,sliceName)
		created_vms = list()
		nodes = list()
		for slivers in requested_attributes:
			for vm in slivers['slivers']:
				node = self.shell.GetNodes(uuid=vm['server-id'])
				if not node in nodes:
					nodes.append(node)
				created_vms.append({'vm-name':vm['name'],'vm-state':'ongoing','slice-name':slice_leaf,'node-name':'Foix'})
		return self.aggregate.get_rspec(slice_leaf=slice_leaf,projectName=projectName,version=rspec.version,created_vms=created_vms,new_nodes=nodes)
	
	def sliver_status(self,slice_leaf,authority,creds,options):

		slice = self.shell.GetSlice(slice_leaf,authority)	
		result = dict()
		List = list()
		for vm in slice['vms']:
    			List.append({'vm-name':vm['vm-name'],'vm-state': vm['vm-state'], 'node-name': vm['node-name']})
		result['virtual-machines'] = List
		return result
			

		
	
