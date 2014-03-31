from foam.sfa.rspecs.rspec import RSpec
from foam.sfa.rspecs.version_manager import VersionManager
from foam.sfa.lib import getAdvertisement

import time

class OFAggregate:

	def __init__(self):
           pass
	def get_rspec(self, version=None, slice_leaf=None, projectName=None, options={}):

        	version_manager = VersionManager()
        	version = version_manager.get_version(version)
		if slice_leaf:
		    #Manifest RSpec will be used when somebody creates an sliver, returning the resources of this AM and the vm(s) requested by the user.
		    rspec_version = version_manager._get_version(version.type, version.version, 'manifest')
		    options['slice'] = slice_leaf
                    of_xml = getManifest(options['slivers'],slice_leaf)
                    rspec = RSpec(version=rspec_version, user_options=options)
                    rspec.version.add_slivers(of_xml)
		else:
        	    rspec_version = version_manager._get_version(version.type, version.version, 'ad')
                    if 'slice_urn' in options.keys() :
                        #TODO add filter
                        pass
		    of_xml = getAdvertisement()
		    rspec = RSpec(version=rspec_version, user_options=options)
                    rspec.version.add_nodes(of_xml)
        	return rspec.toxml()


