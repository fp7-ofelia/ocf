from vt_manager.communication.sfa.util.xrn import Xrn, hrn_to_urn, urn_to_hrn
from vt_manager.communication.sfa.util.sfatime import utcparse, datetime_to_string

from vt_manager.communication.sfa.rspecs.rspec import RSpec
#from vt_manager.communication.sfa.rspecs.elements.hardware_type import HardwareType
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
from vt_manager.communication.sfa.rspecs.elements.ocf_vt_server import OcfVtServer
from vt_manager.communication.sfa.rspecs.version_manager import VersionManager

from vt_manager.communication.sfa.rspecs.elements.range import Range
from vt_manager.communication.sfa.rspecs.elements.network_interface import NetworkInterface
from vt_manager.communication.sfa.rspecs.elements.vm import VM
from vt_manager.communication.sfa.rspecs.elements.vm_interface import VMInterface

#from sfa.dummy.dummyxrn import DummyXrn, hostname_to_urn, hrn_to_dummy_slicename, slicename_to_hrn

from vt_manager.communication.sfa.VTShell import VTShell

import time

#XXX: this class should be like a RspecManager? Should call the VTShell or it should be called in the VTDriver?
class VMAggregate:

	def __init__(self):
		self.shell = VTShell()
	
	def get_rspec(self, version=None, slice_leaf=None, options={}):

		#XXX: I think this is quite clear
        	version_manager = VersionManager()
        	version = version_manager.get_version(version)
		if slice_leaf:
		    #Manifest RSpec will be used when somebody creates an sliver, returning the resources of this AM and the vm(s) requested by the user.
		    rspec_version = version_manager._get_version(version.type, version.version, 'manifest')
		    options['slice']=slice_leaf
		else:
        	    rspec_version = version_manager._get_version(version.type, version.version, 'ad')

        	rspec = RSpec(version=rspec_version, user_options=options)

        	nodes = self.get_nodes(options,slice_leaf)
        	rspec.version.add_nodes(nodes)
        	return rspec.toxml()
	
    	def get_nodes(self, options={},slice_leaf = None):

		if 'slice' in options.keys():
			nodes = self.shell.GetNodes(options['slice'])
		else:
	        	nodes = self.shell.GetNodes()
	        rspec_nodes = []
	        for node in nodes:
		    
	            rspec_node = Node()
	            site=self.get_testbed_info()
		    #TODO: Get HRNs URNs from OFELIA site or use the method get_leaf() from xrns
		    #TODO: Define some kind of Hostnames
	            rspec_node['component_id'] = node.uuid#hostname_to_urn(self.driver.hrn, site['name'], node['hostname'])
	            rspec_node['component_name'] = node.name#node['hostname']
	            rspec_node['component_manager_id'] = 'ocf.i2cat.vtmanager:'+node.uuid+'authority+cm'#Xrn(self.driver.hrn, 'authority+cm').get_urn()
        	    rspec_node['authority_id'] = 'urn:publicid:IDN+i2cat.net+authority+sa' #hrn_to_urn(DummyXrn.site_hrn(self.driver.hrn, site['name']), 'authority+sa')
	            rspec_node['exclusive'] = 'false'
	            rspec_node['hardware_types'] = [OcfVtServer({'name':str(node.name),
								 'operating_system_type':str(node.operatingSystemType),
								 'operating_system_distribution':str(node.operatingSystemDistribution),
								 'operating_system_version':str(node.operatingSystemVersion),
								 'virtualization_technology':node.virtTech,
								 'cpus_number':str(node.numberOfCPUs),
								 'cpu_frequency':str(node.CPUFrequency),
								 'memory':str(node.memory),
								 'hdd_space_GB':str(node.discSpaceGB),
								 'agent_url':str(node.agentURL), })]
		    #XXX: I' don't like it
		    ip_ranges = node.subscribedIp4Ranges.all()
		    mac_ranges = node.subscribedMacRanges.all()
		    network_ifaces = node.networkInterfaces.all()
		    #XXX: I use services because it works well
		    rspec_node['services'] = list()
		    if ip_ranges:
			     for ip_range in ip_ranges:
			     	rspec_node['services'].append(Range({'type':'IP_Range',
          				       			     'name':ip_range.name,
							             'start_value': ip_range.startIp,
							             'end_value': ip_range.endIp}))
		    if mac_ranges:
			     for mac_range in mac_ranges:
			     	rspec_node['services'].append(Range({'type':'MAC_Range',
                                                                     'name':mac_range.name,
                                                                     'start_value': mac_range.startMac,
                                                                     'end_value': mac_range.endMac}))
		    if network_ifaces:
			     for network_iface in network_ifaces:
			    	rspec_node['services'].append(NetworkInterface({'from_server_interface_name':network_iface.name,
				    					        'to_network_interface_id': network_iface.switchID,
										'to_network_interface_port':str(network_iface.port)}))
                    if site['longitude'] and site['latitude']:
    	                location = Location({'longitude': site['longitude'], 'latitude': site['latitude'], 'country': 'unknown'})
        	        rspec_node['location'] = location
		
		    #TODO:complete slivers part for manifest RSpecs
		    slices = self.shell.GetSlice(slice_leaf)
		    slivers = list()
		    if slices:
		        for vm in slices['vms']:
			    if vm['node-name'] == node.name:
		    	    	slivers.append(VM({'name':vm['vm-name'],
			        	           'state':vm['vm-state'],
						  }))
			rspec_node['slivers'] = slivers
		
            	    rspec_nodes.append(rspec_node)
        	return rspec_nodes

	def get_testbed_info(self):
		#TODO: get True Testbed Info from the AM
		return {'longitude':None,'latitude':None}

