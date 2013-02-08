from vt_manager.communication.sfa.util.xrn import Xrn, hrn_to_urn, urn_to_hrn
from vt_manager.communication.sfa.util.sfatime import utcparse, datetime_to_string
from vt_manager.communication.sfa.util.sfalogging import logger

from vt_manager.communication.sfa.rspecs.rspec import RSpec
from vt_manager.communication.sfa.rspecs.elements.hardware_type import HardwareType
from vt_manager.communication.sfa.rspecs.elements.node import Node
from vt_manager.communication.sfa.rspecs.elements.link import Link
from vt_manager.communication.sfa.rspecs.elements.sliver import Sliver
from vt_manager.communication.sfa.rspecs.elements.login import Login
from vt_manager.communication.sfa.rspecs.elements.location import Location
from vt_manager.communication.sfa.rspecs.elements.interface import Interface
from vt_manager.communication.sfa.rspecs.elements.services import Services
from vt_manager.communication.sfa.rspecs.elements.pltag import PLTag
from vt_manager.communication.sfa.rspecs.elements.lease import Lease
from vt_manager.communication.sfa.rspecs.elements.granularity import Granularity
from vt_manager.communication.sfa.rspecs.version_manager import VersionManager

#from sfa.dummy.dummyxrn import DummyXrn, hostname_to_urn, hrn_to_dummy_slicename, slicename_to_hrn

from vt_manager.communication.VTShell import VTShell

import time

class VMAggregate:

	def __init__(self):
		pass
	
	def get_rspec(self, version = None, options={}):

		#XXX: I think this is quite clear
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
	            site=self.get_testbed_info()
		    #TODO: Get HRNs URNs from OFELIA site
		    #TODO: Define some kind of Hostnames
	            rspec_node['component_id'] = node.uuid#hostname_to_urn(self.driver.hrn, site['name'], node['hostname'])
	            rspec_node['component_name'] = node.name#node['hostname']
	            rspec_node['component_manager_id'] = 'ocf.i2cat.vtmanager:'+node.uuid+'authority+cm'#Xrn(self.driver.hrn, 'authority+cm').get_urn()
        	    rspec_node['authority_id'] = 'urn:publicid:IDN+i2cat.net+authority+cm' #hrn_to_urn(DummyXrn.site_hrn(self.driver.hrn, site['name']), 'authority+sa')
	            rspec_node['exclusive'] = 'false'
	            rspec_node['hardware_types'] = [HardwareType({'name': 'xenServer'}), HardwareType({'name': 'server'})]
	             # add site/interface info to nodes.
        	    # assumes that sites, interfaces and tags have already been prepared.
                if site['longitude'] and site['latitude']:
    	            location = Location({'longitude': site['longitude'], 'latitude': site['latitude'], 'country': 'unknown'})
        	    rspec_node['location'] = location


                # slivers always provide the ssh service
                #login = Login({'authentication': 'ssh-keys', 'hostname': node['hostname'], 'port':'22', 'username': slice['slice_name']})
                #service = Services({'login': login})
                #rspec_node['services'] = [service]
            	rspec_nodes.append(rspec_node)
        	return rspec_nodes

	def get_tesbed_info(self):
		#TODO: get True Testbed Info from the AM
		return {}

