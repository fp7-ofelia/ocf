from openflow.optin_manager.sfa.util.xrn import Xrn, hrn_to_urn, urn_to_hrn
from openflow.optin_manager.sfa.rspecs.rspec import RSpec
from openflow.optin_manager.sfa.rspecs.elements.node import Node
from openflow.optin_manager.sfa.rspecs.elements.login import Login
from openflow.optin_manager.sfa.rspecs.version_manager import VersionManager
from openflow.optin_manager.sfa.openflow_utils.foam_rspec_lib import getAdvertisement, getManifest
from openflow.optin_manager.sfa.drivers.OFShell import OFShell

import time

class OFAggregate:

	def __init__(self):
		self.shell = OFShell()

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
		        nodes = self.shell.GetNodes(options['slice_urn'])
                    else:
                        nodes = self.shell.GetNodes()
		    of_xml = getAdvertisement(nodes)
		    rspec = RSpec(version=rspec_version, user_options=options)
                    rspec.version.add_nodes(of_xml)
        	return rspec.toxml()

        #XXX:deprecated	
    	def get_nodes(self, options={},slice_leaf = None,projectName=None):
		if 'slice' in options.keys():
			nodes = self.shell.GetNodes(options['slice'],projectName)
		else:
	        	nodes = self.shell.GetNodes()
	        rspec_nodes = []
	        for node in nodes:
	            rspec_node = Node()
	            site=self.get_testbed_info()
		    rspec_node['hostname'] = 'optin.i2cat.net'
	            rspec_node['exclusive'] = 'false'
	            rspec_node['hardware_types'] = [OpenFlowSitch({'component_id':  hrn_to_urn('ocf.i2cat.vt_manager' + '.' + node['dpid'], 'node'),
								   'component_manager_id': hrn_to_urn('ocf.i2cat.optin_manager','authority'),
							 	   'dpid':node['dpid'],
								   'port':node['ports']
								  })]
		    if slice_leaf:
			slices = (self.shell.GetSlice(slice_leaf,projectName))
			rspec_node['slivers'] = slices
		
            	    rspec_nodes.append(rspec_node)
        	return rspec_nodes

	def get_testbed_info(self):
		#TODO: get True Testbed Info from the AM
		return {'longitude':None,'latitude':None}

