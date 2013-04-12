from openflow.optin_manager.sfa.util.xrn import Xrn, hrn_to_urn, urn_to_hrn
from openflow.optin_manager.sfa.util.sfatime import utcparse, datetime_to_string

from openflow.optin_manager.sfa.rspecs.rspec import RSpec
#from openflow.optin_manager.sfa.rspecs.elements.hardware_type import HardwareType
from openflow.optin_manager.sfa.rspecs.elements.node import Node
from openflow.optin_manager.sfa.rspecs.elements.link import Link
from openflow.optin_manager.sfa.rspecs.elements.sliver import Sliver
from openflow.optin_manager.sfa.rspecs.elements.login import Login
from openflow.optin_manager.sfa.rspecs.elements.location import Location
from openflow.optin_manager.sfa.rspecs.elements.interface import Interface
from openflow.optin_manager.sfa.rspecs.elements.services import Services
from openflow.optin_manager.sfa.rspecs.elements.pltag import PLTag
from openflow.optin_manager.sfa.rspecs.elements.lease import Lease
from openflow.optin_manager.sfa.rspecs.elements.granularity import Granularity
from openflow.optin_manager.sfa.rspecs.elements.ocf_vt_server import OcfVtServer
from openflow.optin_manager.sfa.rspecs.version_manager import VersionManager

from openflow.optin_manager.sfa.openflow_utils.foam_rspec_lib import getAdvertisement

#from sfa.dummy.dummyxrn import DummyXrn, hostname_to_urn, hrn_to_dummy_slicename, slicename_to_hrn

from openflow.optin_manager.sfa.OFShell import OFShell

import time

class OFAggregate:

	def __init__(self):
		self.shell = OFShell()

	@staticmethod
	def FilterList(myfilter, mylist):
    		result = []
    		result.extend(mylist)
    		for item in mylist:
         		for key in myfilter.keys():
                 		if myfilter[key] != item[key]:
                     			result.remove(item)
              			        break
    		return result

	
	def get_rspec(self, version=None, slice_leaf=None, projectName=None, options={}):

        	version_manager = VersionManager()
        	version = version_manager.get_version(version)
		if slice_leaf:
		    #Manifest RSpec will be used when somebody creates an sliver, returning the resources of this AM and the vm(s) requested by the user.
		    rspec_version = version_manager._get_version(version.type, version.version, 'manifest')
		    options['slice']=slice_leaf
		else:
        	    rspec_version = version_manager._get_version(version.type, version.version, 'ad')
		    nodes = self.shell.GetNodes()
		    of_xml = getAdvertisement(nodes)
		    
        	rspec = RSpec(version=rspec_version, user_options=options)
        	#nodes = self.get_nodes(options,slice_leaf,projectName)
        	rspec.version.add_nodes(of_xml)
        	return rspec.toxml()
	
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

