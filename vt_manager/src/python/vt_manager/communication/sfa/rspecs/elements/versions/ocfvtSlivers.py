from vt_manager.communication.sfa.rspecs.elements.element import Element
from vt_manager.communication.sfa.rspecs.elements.sliver import Sliver
from vt_manager.communication.sfa.rspecs.elements.vm import VM
from vt_manager.communication.sfa.rspecs.elements.vm_interface import VMInterface
from vt_manager.communication.sfa.rspecs.elements.versions.pgv2DiskImage import PGv2DiskImage
from vt_manager.communication.sfa.rspecs.elements.versions.plosv1FWRule import PLOSv1FWRule

class OcfVtSlivers:

    @staticmethod
    def add_slivers(xml, slivers):
        if not slivers:
            return 
        if not isinstance(slivers, list):
            slivers = [slivers]
        for sliver in slivers: 
            sliver_elem = xml.add_element('sliver_type')
            if sliver.get('type'):
                sliver_elem.set('name', sliver['type'])
            attrs = ['client_id', 'cpus', 'memory', 'storage']
            for attr in attrs:
                if sliver.get(attr):
                    sliver_elem.set(attr, sliver[attr])
            
            images = sliver.get('disk_image')
            if images and isinstance(images, list):
                PGv2DiskImage.add_images(sliver_elem, images)      
            fw_rules = sliver.get('fw_rules')
            if fw_rules and isinstance(fw_rules, list):
                PLOSv1FWRule.add_rules(sliver_elem, fw_rules)
            PGv2SliverType.add_sliver_attributes(sliver_elem, sliver.get('tags', []))
    
    @staticmethod
    def add_sliver_attributes(xml, attributes):
        if attributes: 
            for attribute in attributes:
                if attribute['name'] == 'initscript':
                    xml.add_element('{%s}initscript' % xml.namespaces['planetlab'], name=attribute['value'])
                elif attribute['tagname'] == 'flack_info':
                    attrib_elem = xml.add_element('{%s}info' % self.namespaces['flack'])
                    attrib_dict = eval(tag['value'])
                    for (key, value) in attrib_dict.items():
                        attrib_elem.set(key, value)                
    @staticmethod
    def get_slivers(sliver_elems, filter={}):
        #xpath = './default:sliver_type | ./sliver_type'
        #sliver_elems = xml.xpath(xpath)
	#XXX: We have virtual-machines here
        slivers = []
        for sliver_elem in sliver_elems:
            sliver = VM()
	    vm_attrs = sliver.fields
	    if 'interfaces' in vm_attrs:
	        vm_ifaces = vm_attrs.pop(vm_attrs.index('interfaces'))
	    for sliver_attr in sliver_elem:
		if sliver_attr.tag == 'interfaces':
		    sliver[sliver_attr.tag] = OcfVtSlivers.get_interfaces(list(sliver_attr))

		elif sliver_attr.tag in vm_attrs and sliver_attr.text:
		    sliver[sliver_attr.tag] = sliver_attr.text	

		else:
		    continue
		
	    slivers.append(sliver)	
        return slivers
	
    @staticmethod
    def get_interfaces(interfaces):
	ifaces = list()
	for interface in interfaces:
	    iface = VMInterface()
	    if interface.attrib:
	        iface.update(interface.attrib)
	    for iface_attr in interface:
	        if iface_attr.tag in iface.fields and iface_attr.text:
		    iface[iface_attr.tag] = iface_attr.text
	    ifaces.append(iface)
	return ifaces

    @staticmethod
    def get_sliver_attributes(xml, filter={}):
        return []             
