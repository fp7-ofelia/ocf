    @staticmethod
    def setVMinterfaces(VMmodel, VMxmlClass):
        #eth0 is reserved for the management interface
        ethIndex = 1
        for iface in VMxmlClass.xen_configuration.interfaces.interface:
        for i, ServerIface in enumerate(VTServer.objects.get(uuid = VMmodel.getServerID()).ifaces.all()):
            if i != 0:
                newInterface = copy.deepcopy(VMxmlClass.xen_configuration.interfaces.interface[0])
                newInterface = VMxmlClass.xen_configuration.interfaces.interface.append(newInterface)
            else:
                newInterface = VMxmlClass.xen_configuration.interfaces.interface[0]

            newInterface.name = VTServer.objects.get(uuid = VMmodel.getServerID()).ifaces.'eth'+str(ethIndex)
            iface.mac = MACallocator.acquire(VMxmlClass.project_id, 1, VMxmlClass.slice_id, VMxmlClass.uuid, iface.name)



            if iface.ismgmt is True:
                #iface.name = 'eth'+str(ethIndex)
                iface.name = VTServer.objects.get(uuid = VMmodel.getServerID()).getVmMgmtIface()
                iface.mac = MACallocator.acquire(VMxmlClass.project_id, 1, VMxmlClass.slice_id, VMxmlClass.uuid, iface.name, True)
                iptemp = IPallocator.acquire(VMxmlClass.server_id, VMxmlClass.project_id, 1, VMxmlClass.slice_id, VMxmlClass.uuid, iface.name, True)
                iface.ip = iptemp.ip
                iface.mask = iptemp.mask
                iface.gw = iptemp.gw
                iface.dns1 = iptemp.dns1
                iface.dns2 = iptemp.dns2
                #Relate the IPs created with the VMmodel
                try:
                    VMmodel.setIPs()
                except Exception as e:
                    print e
                    raise e

                print "[DEBUG] Management Interface set"
            else:
                iface.name = VTServer.objects.get(uuid = VMmodel.getServerID()).ifaces.'eth'+str(ethIndex)
                iface.mac = MACallocator.acquire(VMxmlClass.project_id, 1, VMxmlClass.slice_id, VMxmlClass.uuid, iface.name)
                print "[DEBUG] Non Management Interface set"
            ethIndex = ethIndex + 1
        #Relate the Macs created with the VMmodel
        VMmodel.setMacs()
