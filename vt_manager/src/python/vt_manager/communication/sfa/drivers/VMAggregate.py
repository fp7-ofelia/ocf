from vt_manager.communication.sfa.util.xrn import Xrn, hrn_to_urn, urn_to_hrn
from vt_manager.communication.sfa.util.sfatime import utcparse, datetime_to_string

from vt_manager.communication.sfa.sfa_config import config

from vt_manager.communication.sfa.rspecs.rspec import RSpec
from vt_manager.communication.sfa.rspecs.elements.node import Node
from vt_manager.communication.sfa.rspecs.elements.sliver import Sliver
from vt_manager.communication.sfa.rspecs.elements.location import Location
from vt_manager.communication.sfa.rspecs.elements.interface import Interface
from vt_manager.communication.sfa.rspecs.elements.services import Services
from vt_manager.communication.sfa.rspecs.elements.ocf_vt_server import OcfVtServer
from vt_manager.communication.sfa.rspecs.version_manager import VersionManager

from vt_manager.communication.sfa.rspecs.elements.range import Range
from vt_manager.communication.sfa.rspecs.elements.network_interface import NetworkInterface
from vt_manager.communication.sfa.rspecs.elements.vm import VM
from vt_manager.communication.sfa.rspecs.elements.vm_interface import VMInterface

from vt_manager.communication.sfa.drivers.VTShell import VTShell

import time

class VMAggregate:

	def __init__(self):
		self.shell = VTShell()

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

	
	def get_rspec(self, version=None, slice_leaf=None, projectName=None ,created_vms=[],new_nodes=[], options={}):

        	version_manager = VersionManager()
        	version = version_manager.get_version(version)
		if slice_leaf:
		    #Manifest RSpec will be used when somebody creates an sliver, returning the resources of this AM and the vm(s) requested by the user.
		    rspec_version = version_manager._get_version(version.type, version.version, 'manifest')
		    options['slice']=slice_leaf
		else:
        	    rspec_version = version_manager._get_version(version.type, version.version, 'ad')

        	rspec = RSpec(version=rspec_version, user_options=options)

        	nodes = self.get_nodes(options,slice_leaf,projectName,created_vms,new_nodes)
        	rspec.version.add_nodes(nodes)
        	return rspec.toxml()
	
    	def get_nodes(self, options={},slice_leaf = None,projectName=None,created_vms=[],new_nodes=[]):
		if 'slice' in options.keys():
			nodes = self.shell.GetNodes(options['slice'],projectName)
			if not nodes:
				nodes = new_nodes
		else:
	        	nodes = self.shell.GetNodes()
	        rspec_nodes = []
	        for node in nodes:
		    
	            rspec_node = Node()
	            site=self.get_testbed_info()
	            rspec_node['component_id'] = hrn_to_urn(config.HRN+'.'+str(node.name),'node')
	            rspec_node['component_name'] = node.name
	            rspec_node['component_manager_id'] = "urn:publicid:IDN+" + config.OCF_ISLAND_AUTHORITY + ":" + config.OCF_AM_TYPE + "+cm"
		    rspec_node['hostname'] = str(node.name).lower() + '.ctx.i2cat.net'
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
		    if not slice_leaf:
		    	ip_ranges = node.subscribedIp4Ranges.all()
		    	mac_ranges = node.subscribedMacRanges.all()
		    	network_ifaces = node.networkInterfaces.all()
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
		
		    slices = list()
		    cVMs = dict()
		    if slice_leaf:
			slices = (self.shell.GetSlice(slice_leaf,projectName))
		    	slices['vms'].extend(VMAggregate.FilterList({'slice-name':slice_leaf,'node-name':node.name},created_vms))
			#cVMs['vms'] = createdVMs
		    slivers = list() 
		    if slices:
		        for vm in slices['vms']:
			    if vm['node-name'] == node.name:
		    	    	slivers.append(VM({'name':vm['vm-name'],
			        	           'state':vm['vm-state'],
                                                   'ip':vm['vm-ip'],
						  }))
			rspec_node['slivers'] = slivers
		
            	    rspec_nodes.append(rspec_node)
        	return rspec_nodes

	def get_testbed_info(self):
		#TODO: get True Testbed Info from the AM
		return {'longitude':None,'latitude':None}

