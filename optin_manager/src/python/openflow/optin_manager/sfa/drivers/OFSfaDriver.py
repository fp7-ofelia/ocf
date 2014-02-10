import time

import datetime
from openflow.optin_manager.sfa.util.faults import MissingSfaInfo, UnknownSfaType, \
    RecordNotFound, SfaNotImplemented, SliverDoesNotExist

from openflow.optin_manager.sfa.util.defaultdict import defaultdict
from openflow.optin_manager.sfa.util.sfatime import utcparse, datetime_to_string, datetime_to_epoch
from openflow.optin_manager.sfa.util.xrn import Xrn, hrn_to_urn, get_leaf
from openflow.optin_manager.sfa.util.cache import Cache
from openflow.optin_manager.sfa.trust.credential import Credential

from openflow.optin_manager.sfa.rspecs.version_manager import VersionManager
from openflow.optin_manager.sfa.rspecs.rspec import RSpec

from openflow.optin_manager.sfa.drivers.OFAggregate import OFAggregate
from openflow.optin_manager.sfa.drivers.OFShell import OFShell

class OFSfaDriver:

	def __init__ (self, config=None):
		self.aggregate = OFAggregate()
		self.shell = OFShell()

	def list_resources (self,slice_urn=None, slice_leaf=None, creds=[], options={},):

		version_manager = VersionManager()
		rspec_version = 'OcfOf'
        	version_string = "rspec_%s" % (rspec_version)
                if slice_urn:
                    options['slice_urn'] = slice_urn
	        rspec =  self.aggregate.get_rspec(version=rspec_version,options=options)
       		return rspec

	def crud_slice (self,slice_urn,authority,action=None):

                try:
		    if action == 'start_slice':
		        self.shell.StartSlice(slice_urn)
		    elif action == 'stop_slice':
			self.shell.StopSlice(slice_urn)
	       	    elif action == 'delete_slice':
			self.shell.DeleteSlice(slice_urn)
		    elif action == 'reset_slice':
			self.shell.RebootSlice(slice_urn)

                    return 1

                except Exception as e:
                        raise RecordNotFound(slice_urn)
	

        def create_sliver (self,slice_urn,slice_leaf,authority,rspec_string, users, options, expiration):
                rspec = RSpec(rspec_string,'OcfOf')
                requested_attributes = rspec.version.get_slice_attributes()
		projectName = authority
		sliceName = slice_leaf
		self.shell.CreateSliver(requested_attributes,slice_urn,projectName,expiration)
	        options['slivers'] = requested_attributes
            	
		return self.aggregate.get_rspec(slice_leaf=slice_leaf,projectName=projectName,version=rspec.version,options=options)
	
	def sliver_status(self,slice_urn,authority,options):
		result = self.shell.SliverStatus(slice_urn)
		return result

        def get_expiration_date(self,slice_hrn, creds):
        	for cred in creds:
                	credential = Credential(string=cred)
                    	if credential.get_gid_caller().get_hrn() == slice_hrn:
                        	return credential.get_expiration()
                return None 
                	
		
	

