import copy


class Translator:

    @staticmethod
    def VMdictToClass(VMdict, VMxmlClass):
      
        VMxmlClass.name = VMdict['name']
        VMxmlClass.uuid = VMdict['uuid']
        VMxmlClass.status = VMdict['state']
        VMxmlClass.project_id = VMdict['project-id']
        VMxmlClass.project_name = VMdict['project-name']
        VMxmlClass.slice_id = VMdict['slice-id']
        VMxmlClass.slice_name = VMdict['slice-name']
        VMxmlClass.operating_system_type = VMdict['operating-system-type']
        VMxmlClass.operating_system_version = VMdict['operating-system-version']
        VMxmlClass.operating_system_distribution = VMdict['operating-system-distribution']
        VMxmlClass.virtualization_type = VMdict['virtualization-type']
        VMxmlClass.server_id = VMdict['server-id']
        VMxmlClass.xen_configuration.hd_setup_type = VMdict['hd-setup-type']
        VMxmlClass.xen_configuration.hd_origin_path = VMdict['hd-origin-path']
        VMxmlClass.xen_configuration.virtualization_setup_type = VMdict['virtualization-setup-type']
        VMxmlClass.xen_configuration.memory_mb = int(VMdict['memory-mb'])


    @staticmethod
    def VMdicIfacesToClass(ifaces, IfaceXmlClass):
	
#	ifaceClassEmpty = copy.deepcopy(IfaceXmlClass.interface[0])
	#IfaceXmlClass.interface.pop()
        if not ifaces:
            ifaces = []
            iface = dict()
            iface['gw'] = None
            iface['mac'] = None
            iface['name'] = None
            iface['dns1'] = None
            iface['dns2'] = None
            iface['ip'] = None
            iface['mask'] = None               
            ifaces.append(iface)

	for iface in ifaces:
	    ifaceClassEmpty = copy.deepcopy(IfaceXmlClass.interface[0])
	    ifaceClassEmpty.gw = iface['gw']
	    ifaceClassEmpty.mac = iface['mac']
	    ifaceClassEmpty.name = iface['name']
	    ifaceClassEmpty.dns1 = iface['dns1']
	    ifaceClassEmpty.dns2 = iface['dns2']
	    ifaceClassEmpty.ip = iface['ip']
	    ifaceClassEmpty.mask = iface['mask']
	    if 'ismgmt' in iface.keys():
	    	ifaceClassEmpty.ismgmt = iface['ismgmt']
	    else:
		ifaceClassEmpty.ismgmt = 'false'
		
            IfaceXmlClass.interface.append(ifaceClassEmpty)

        IfaceXmlClass.interface.pop(0) # Deleting the empty interface instance       

 	
