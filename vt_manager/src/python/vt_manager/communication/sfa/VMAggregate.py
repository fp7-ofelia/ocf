from sfa.util.xrn import Xrn, hrn_to_urn, urn_to_hrn
from sfa.util.sfatime import utcparse, datetime_to_string
from sfa.util.sfalogging import logger

from sfa.rspecs.rspec import RSpec
from sfa.rspecs.elements.hardware_type import HardwareType
from sfa.rspecs.elements.node import Node
from sfa.rspecs.elements.link import Link
from sfa.rspecs.elements.sliver import Sliver
from sfa.rspecs.elements.login import Login
from sfa.rspecs.elements.location import Location
from sfa.rspecs.elements.interface import Interface
from sfa.rspecs.elements.services import Services
from sfa.rspecs.elements.pltag import PLTag
from sfa.rspecs.elements.lease import Lease
from sfa.rspecs.elements.granularity import Granularity
from sfa.rspecs.version_manager import VersionManager

#from sfa.dummy.dummyxrn import DummyXrn, hostname_to_urn, hrn_to_dummy_slicename, slicename_to_hrn

from VTShell import VTShell

import time

class VMAggregate:

	def __init__(self):
		pass
	
	def get_rspec(self, version = None, options={}):

        	version_manager = VersionManager()
        	version = version_manager.get_version(version)
        	rspec_version = version_manager._get_version(version.type, version.version, 'ad')

        	rspec = RSpec(version=rspec_version, user_options=options)

        	nodes = self.get_nodes(options)
        	rspec.version.add_nodes(nodes)

        	return rspec.toxml()
	

    	def get_nodes(self, options={}):

	        nodes = VTShell.GetNodes()

		#TODO: Mount Rspec
	        rspec_nodes = []
	        for node in nodes:
	            rspec_node = Node()
	            site=self.driver.testbedInfo
	            rspec_node['component_id'] = hostname_to_urn(self.driver.hrn, site['name'], node['hostname'])
	            rspec_node['component_name'] = node['hostname']
	            rspec_node['component_manager_id'] = Xrn(self.driver.hrn, 'authority+cm').get_urn()
        	    rspec_node['authority_id'] = hrn_to_urn(DummyXrn.site_hrn(self.driver.hrn, site['name']), 'authority+sa')
	            rspec_node['exclusive'] = 'false'
	            rspec_node['hardware_types'] = [HardwareType({'name': 'plab-pc'}), HardwareType({'name': 'pc'})]
	             # add site/interface info to nodes.
        	    # assumes that sites, interfaces and tags have already been prepared.
                if site['longitude'] and site['latitude']:
    	            location = Location({'longitude': site['longitude'], 'latitude': site['latitude'], 'country': 'unknown'})
        	    rspec_node['location'] = location

            	if node['node_id'] in slivers:
                    # add sliver info
    	            sliver = slivers[node['node_id']]
                    rspec_node['client_id'] = node['hostname']
        	    rspec_node['slivers'] = [sliver]

                # slivers always provide the ssh service
                login = Login({'authentication': 'ssh-keys', 'hostname': node['hostname'], 'port':'22', 'username': slice['slice_name']})
                service = Services({'login': login})
                rspec_node['services'] = [service]
            	rspec_nodes.append(rspec_node)
        	return rspec_nodes


