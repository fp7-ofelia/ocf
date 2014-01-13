import copy

class Translator:
    @staticmethod
    def vm_dict_to_class(vm_dict, vm_xml_class):
        vm_xml_class.name = vm_dict['name']
        vm_xml_class.uuid = vm_dict['uuid']
        vm_xml_class.status = vm_dict['state']
        vm_xml_class.project_id = vm_dict['project-id']
        vm_xml_class.project_name = vm_dict['project-name']
        vm_xml_class.slice_id = vm_dict['slice-id']
        vm_xml_class.slice_name = vm_dict['slice-name']
        vm_xml_class.operating_system_type = vm_dict['operating-system-type']
        vm_xml_class.operating_system_version = vm_dict['operating-system-version']
        vm_xml_class.operating_system_distribution = vm_dict['operating-system-distribution']
        vm_xml_class.virtualization_type = vm_dict['virtualization-type']
        vm_xml_class.server_id = vm_dict['server-id']
        vm_xml_class.xen_configuration.hd_setup_type = vm_dict['hd-setup-type']
        vm_xml_class.xen_configuration.hd_origin_path = vm_dict['hd-origin-path']
        vm_xml_class.xen_configuration.virtualization_setup_type = vm_dict['virtualization-setup-type']
        vm_xml_class.xen_configuration.memory_mb = int(vm_dict['memory-mb'])
    
    @staticmethod
    def vm_dic_ifaces_to_class(ifaces, iface_xml_class):
#        iface_class_empty = copy.deepcopy(iface_xml_class.interface[0])
        #iface_xml_class.interface.pop()
        for iface in ifaces:
            iface_class_empty = copy.deepcopy(iface_xml_class.interface[0])
            iface_class_empty.gw = iface['gw']
            iface_class_empty.mac = iface['mac']
            iface_class_empty.name = iface['name']
            iface_class_empty.dns1 = iface['dns1']
            iface_class_empty.dns2 = iface['dns2']
            iface_class_empty.ip = iface['ip']
            iface_class_empty.mask = iface['mask']
            if 'ismgmt' in iface.keys():
                iface_class_empty.ismgmt = iface['ismgmt']
            else:
                iface_class_empty.ismgmt = 'false'
            iface_xml_class.interface.append(iface_class_empty)
        iface_xml_class.interface.pop(0) # Deleting the empty interface instance       
