import time

import datetime

from foam.sfa.rspecs.version_manager import VersionManager
from foam.sfa.rspecs.rspec import RSpec

from foam.sfa.drivers.OFAggregate import OFAggregate

class OFSfaDriver:

	def __init__ (self, config=None):
		self.aggregate = OFAggregate()

	def list_resources (self,slice_urn=None, slice_leaf=None, creds=[], options={},):

		version_manager = VersionManager()
		rspec_version = 'OcfOf'
        	version_string = "rspec_%s" % (rspec_version)
                if slice_urn:
                    options['slice_urn'] = slice_urn
	        rspec =  self.aggregate.get_rspec(version=rspec_version,options=options)
       		return rspec

