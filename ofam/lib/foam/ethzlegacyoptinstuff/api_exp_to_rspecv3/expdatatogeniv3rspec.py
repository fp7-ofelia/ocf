#author: Vasileios Kotronis

import sys
import os
from os.path import expanduser

#prepare imports
#import the etree module
from lxml import etree
#import om_ch_translate class from the api to use for the fs field names
#from foam.api.legacyexpedientapi import om_ch_translate
#import some utility functions from flowspaceutils of the legacy optin manager
from foam.ethzlegacyoptinstuff.legacyoptin.flowspaceutils import dotted_ip_to_int, mac_to_int, int_to_dotted_ip, int_to_mac

#needed for the auxiliray function extract_IP_mask_from_IP_range
import operator
import math

def _same(val):
	return "%s" % val 

class om_ch_translate(object): 
  attr_funcs = {
    # attr_name: (func to turn to str, width)
    "dl_src": (int_to_mac, mac_to_int, 48, "mac_src","dl_src"),
    "dl_dst": (int_to_mac, mac_to_int, 48, "mac_dst","dl_dst"),
    "dl_type": (_same, int, 16, "eth_type","dl_type"),
    "vlan_id": (_same, int, 12, "vlan_id","dl_vlan"),
    "nw_src": (int_to_dotted_ip, dotted_ip_to_int, 32, "ip_src","nw_src"),
    "nw_dst": (int_to_dotted_ip, dotted_ip_to_int, 32, "ip_dst","nw_dst"),
    "nw_proto": (_same, int, 8, "ip_proto","nw_proto"),
    "tp_src": (_same, int, 16, "tp_src","tp_src"),
    "tp_dst": (_same, int, 16, "tp_dst","tp_dst"),
    "port_num": (_same, int, 16, "port_number","in_port"),
    }

#transforms an IP1-IP2 expression to an IP/netmask expression (as used in FOAM) 
#IP1 and IP2 are in dotted format ==> yields the minimum range in which IP1 and IP2 are included
def extract_IP_mask_from_IP_range(IP1, IP2):
	splitIP1 = IP1.split('.')
	splitIP2 = IP2.split('.')
	netmaskSize = 32
	for i in range(4):
		xor_current = int(splitIP1[i]) ^ int(splitIP2[i])
		if (xor_current != 0):
			if (xor_current == 1):
				first_diff_bit_num = 1
			elif (xor_current % 2 != 0):
				first_diff_bit_num = int(math.ceil(math.log(xor_current,2)))
			else:
				first_diff_bit_num = int((math.log(xor_current,2)))+1
			netmaskSize = 8*i + 8 - first_diff_bit_num 
			break

	netmask = 0
	for i in range(netmaskSize+1):
		netmask = netmask + 2**(32-i)

	networkIP = int_to_dotted_ip(dotted_ip_to_int(IP1) & netmask)

	return [networkIP, netmaskSize]


#main function for creation of rspec
def create_ofv3_rspec(slice_id, project_name, project_description,
						slice_name, slice_description, controller_url,
						owner_email, owner_password,
						switch_slivers, experimentflowspaces):
	
	#set namespaces
	xmlns = "http://www.geni.net/resources/rspec/3"
	#xmlns = "opt/foam/schemas"
	xs = "http://www.w3.org/2001/XMLSchema-instance"
	#openflow = "http://www.geni.net/resources/rspec/ext/openflow/3"
	openflow = "/opt/ofelia/ofam/schemas"	
	#schemaLocation = "http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/request.xsd http://www.geni.net/resources/rspec/ext/openflow/3 http://www.geni.net/resources/rspec/ext/openflow/3/of-resv.xsd"
	schemaLocation = "http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/request.xsd /opt/ofelia/ofam/schemas /opt/ofelia/ofam/schemas/of-resv-3.xsd"
	
	#initialize the rspec xml with the proper namespaces and set its type to 'request'
	rspec = etree.Element("rspec", attrib={"{"+xs+"}schemaLocation" : schemaLocation, 'type': 'request'}, nsmap={None:xmlns, 'xs':xs, 'openflow':openflow})
	
	#add openflow sliver to rspec
	ofsliver = etree.SubElement(rspec, "{"+openflow+"}sliver")
	ofsliver.set("description", "project:" + project_description + "|slice:" + slice_description)
	ofsliver.set("email", owner_email)
	ofsliver.set("ref", "sample experiment reference")
	
	#add controllers to rspec
	ofcontrollers = []
	for i in range(3):
		ofcontrollers.append(etree.SubElement(ofsliver, "{"+openflow+"}controller"))
	#primary controller
	ofcontrollers[0].set("url", controller_url)
	ofcontrollers[0].set("type", "primary")
	#monitor controller
	ofcontrollers[1].set("url", "tcp:monitor.example.foam.ocf.fp7-ofelia.eu:6634")
	ofcontrollers[1].set("type", "monitor")
	#backup controller
	ofcontrollers[2].set("url", "tcp:backup.example.foam.ocf.fp7-ofelia.eu:6633")
	ofcontrollers[2].set("type", "backup")	
	
	#add sliver group to rspec
	ofgroup = etree.SubElement(ofsliver, "{"+openflow+"}group")
	ofgroup.set("name", slice_name)
	
	#determine the datapaths and ports of the sliver group
	ofdpids = []
	ofdpports = dict()
	
	for experimentflowspace in experimentflowspaces:
		if (experimentflowspace.dpid is None):
			raise Exception("No dpid is specified for this flowspace!")
		#check if we have already registered the datapath
		if (experimentflowspace.dpid in ofdpids) is False:
			ofdpids.append(experimentflowspace.dpid)
			ofdpports[experimentflowspace.dpid] = []
		#now we can associate the ports with the datapath
		if (experimentflowspace.port_number_s is None):
			raise Exception("No port on a dpid is specified for this flowspace!")
		if (experimentflowspace.port_number_e is not None):
			for port_number in xrange(experimentflowspace.port_number_s, experimentflowspace.port_number_e):
				ofdpports[experimentflowspace.dpid].append(port_number)
			ofdpports[experimentflowspace.dpid].append(experimentflowspace.port_number_e) #because range ignores end number
		else:
			ofdpports[experimentflowspace.dpid].append(experimentflowspace.port_number_s)
	
	#add datapaths and ports to rspec	
	ofgroupdatapaths = []
	ofgroupdpports = []
	i=0
	j=0
	for dpid in ofdpids:
		ofgroupdatapaths.append(etree.SubElement(ofgroup, "{"+openflow+"}datapath"))
		#ofgroupatapaths[i].set("component_id", "urn:publicid:IDN+openflow:foam:foam.example.net+datapath+"+str(dpid))
		#ofgroupdatapaths[i].set("component_manager_id", "urn:publicid:IDN+openflow:foam:foam.example.net+authority+am")
		ofgroupdatapaths[i].set("component_id", "urn:publicid:IDN+openflow:foam:fp7-ofelia.eu:ocf+datapath+"+str(dpid)) #careful with site-tag
		ofgroupdatapaths[i].set("component_manager_id", "urn:publicid:IDN+openflow:foam:fp7-ofelia.eu:ocf+authority+am") #careful with site-tag
		for dpp in ofdpports[dpid]: 
			ofgroupdpports.append(etree.SubElement(ofgroupdatapaths[i], "{"+openflow+"}port"))
			ofgroupdpports[j].set("num", str(dpp)) #we will see about the name attribute
			j = j + 1
		i=i+1
		
	#translate experiment flowspaces to "match" structures
	ofmatch = []
	ofmatchdatapaths = []
	ofmatchdpports = []
	ofmatchdppackets = []
	ofmatchdppktfsfields = []
	i = 0
	j = 0
	k = 0
	for experimentflowspace in experimentflowspaces:
		ofmatch.append(etree.SubElement(ofsliver, "{"+openflow+"}match"))
		#match datapath + ports
		ofmatchdatapaths.append(etree.SubElement(ofmatch[i], "{"+openflow+"}datapath"))
		#ofmatchdatapaths[i].set("component_id", "urn:publicid:IDN+openflow:foam:foam.example.net+datapath+"+str(experimentflowspace.dpid))
		#ofmatchdatapaths[i].set("component_manager_id", "urn:publicid:IDN+openflow:foam:foam.example.net+authority+am")
		ofmatchdatapaths[i].set("component_id", "urn:publicid:IDN+openflow:foam:fp7-ofelia.eu:ocf+datapath+"+str(experimentflowspace.dpid))
		ofmatchdatapaths[i].set("component_manager_id", "urn:publicid:IDN+openflow:foam:fp7-ofelia.eu:ocf+authority+am")
		ofmatchdatapaths[i].set("dpid", str(experimentflowspace.dpid))
		if (experimentflowspace.port_number_e is not None):
			for port_number in xrange(experimentflowspace.port_number_s, experimentflowspace.port_number_e):
				ofmatchdpports.append(etree.SubElement(ofmatchdatapaths[i], "{"+openflow+"}port"))
				ofmatchdpports[j].set("num", str(port_number))
				j=j+1
			ofmatchdpports.append(etree.SubElement(ofmatchdatapaths[i], "{"+openflow+"}port"))
			ofmatchdpports[j].set("num", str(experimentflowspace.port_number_e))
			j=j+1
		else:
			ofmatchdpports.append(etree.SubElement(ofmatchdatapaths[i], "{"+openflow+"}port"))
			ofmatchdpports[j].set("num", str(experimentflowspace.port_number_s))
		
		#match packet (flowspace)
		ofmatchdppackets.append(etree.SubElement(ofmatch[i], "{"+openflow+"}packet"))
		for ch_name, (to_str, from_str, width, om_name, of_name) in om_ch_translate.attr_funcs.items():
			if (of_name != "in_port"):	#ignore port number it is already taken into account before
				om_start = "%s_s"%(om_name)
				om_end = "%s_e"%(om_name)
				fieldName = of_name
				fieldValue = ""
				field_start_value_int = getattr(experimentflowspace, om_start)
				field_end_value_int = getattr(experimentflowspace, om_end)
				#full_wildcard_flag = True
				if (field_start_value_int == 0) and (field_end_value_int == (2**width - 1)):
					continue
				if (fieldName is "dl_src"):	
					if len(xrange(field_start_value_int,field_end_value_int)) is 0:	#single value
						fieldValue = int_to_mac(field_start_value_int)
					else:
						for dl_src in xrange(field_start_value_int,field_end_value_int):	#range (discrete values)
							fieldValue = fieldValue + int_to_mac(dl_src) +", "
						fieldValue = fieldValue + int_to_mac(field_end_value_int)
				elif (fieldName is "dl_dst"):
					if len(xrange(field_start_value_int,field_end_value_int)) is 0:	#single value
						fieldValue = int_to_mac(field_start_value_int)
					else:
						for dl_dst in xrange(field_start_value_int,field_end_value_int):	#range (discrete values)
							fieldValue = fieldValue + int_to_mac(dl_dst) +", "	
						fieldValue = fieldValue + int_to_mac(field_end_value_int)
				elif (fieldName is "dl_type"):
					if len(xrange(field_start_value_int,field_end_value_int)) is 0:	#single value
						fieldValue = int_to_mac(field_start_value_int)
					else:
						for dl_type in xrange(field_start_value_int,field_end_value_int): #range (discrete values)
							fieldValue = fieldValue + str(hex(dl_type)) +", " 
						fieldValue = fieldValue + hex(field_end_value_int)
				elif (fieldName is "dl_vlan"):
					if len(xrange(field_start_value_int,field_end_value_int)) is 0: #single value
						fieldValue = str(field_start_value_int)
					else:	#range (continuous)
						fieldValue = str(field_start_value_int) + "-" + str(field_end_value_int)
				elif (fieldName is "nw_proto"):	
					if len(xrange(field_start_value_int,field_end_value_int)) is 0: #single value
						fieldValue = str(field_start_value_int)
					else:	#range (continuous)
						fieldValue = str(field_start_value_int) + "-" + str(field_end_value_int)
				elif (fieldName is "nw_src"):	#translate from "-" range to "/" : network address plus netmask
					[netIP, netBitNum] = extract_IP_mask_from_IP_range(int_to_dotted_ip(field_start_value_int), int_to_dotted_ip(field_end_value_int))
					fieldValue = netIP + "/" + str(netBitNum)
				elif (fieldName is "nw_dst"):	#translate from "-" range to "/" : network address plus netmask
					[netIP, netBitNum] = extract_IP_mask_from_IP_range(int_to_dotted_ip(field_start_value_int), int_to_dotted_ip(field_end_value_int))
					fieldValue = netIP + "/" + str(netBitNum)
				elif (fieldName is "tp_src"):
					if len(xrange(field_start_value_int,field_end_value_int)) is 0: #single value
						fieldValue = str(field_start_value_int)
					else:	#range (continuous)
						fieldValue = str(field_start_value_int) + "-" + str(field_end_value_int)
				elif (fieldName is "tp_dst"):
					if len(xrange(field_start_value_int,field_end_value_int)) is 0: #single value
						fieldValue = str(field_start_value_int)
					else:	#range (continuous)
						fieldValue = str(field_start_value_int) + "-" + str(field_end_value_int)
				
				#assign the proper values to fields
				ofmatchdppktfsfields.append(etree.SubElement(ofmatchdppackets[i], "{"+openflow+"}"+fieldName))
				ofmatchdppktfsfields[k].set("value", fieldValue)
				k = k + 1
		i = i+1
			
	#store final rspec for debugging purposes
	string_rspec = etree.tostring(rspec,encoding='UTF-8',xml_declaration=True, pretty_print=True)  
	
# file_dir_path = "~/debug_rspecs_created/"
#	if not os.path.exists(file_dir_path): 
#		os.makedirs(file_dir_path)
#	filename = str(slice_id) + '.rspec' 
#	f = open(os.path.join(file_dir_path, filename), 'w')
#	f.write(string_rspec)
#	f.close()

	#return rspec as a string
	return string_rspec
	
