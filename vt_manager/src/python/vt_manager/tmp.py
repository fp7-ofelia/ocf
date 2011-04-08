    @staticmethod
    def setVMinterfaces(VMmodel, VMxmlClass):
        #Data interfaces
        for i, ServerIface in enumerate(VTServer.objects.get(uuid = VMmodel.getServerID()).ifaces.all()):
            if i != 0:
                newInterface = copy.deepcopy(VMxmlClass.xen_configuration.interfaces.interface[0])
                newInterface = VMxmlClass.xen_configuration.interfaces.interface.append(newInterface)
            else:
                newInterface = VMxmlClass.xen_configuration.interfaces.interface[0]
            newInterface.ismgmt = False
            newInterface.name = 'eth'+str(i+1)
            newInterface.mac = MACallocator.acquire(VMxmlClass.project_id, 1, VMxmlClass.slice_id, VMxmlClass.uuid, newInterface.name)
            newInterface.switch_id = ServerIface.ifaceName 
        #Mgmt Interface
        newInterface = copy.deepcopy(VMxmlClass.xen_configuration.interfaces.interface[0])
        newInterface = VMxmlClass.xen_configuration.interfaces.interface.append(newInterface)
        newInterface.ismgmt = True
        newInterface.name = VTServer.objects.get(uuid = VMmodel.getServerID()).getVmMgmtIface()
        newInterface.mac = MACallocator.acquire(VMxmlClass.project_id, 1, VMxmlClass.slice_id, VMxmlClass.uuid, newInterface.name, True)
        newInterface.switch_id = VTServer.objects.get(uuid = VMmodel.getServerID()).getVmMgmtIface()
        iptemp = IPallocator.acquire(VMxmlClass.server_id, VMxmlClass.project_id, 1, VMxmlClass.slice_id, VMxmlClass.uuid, newInterface.name, True)
        newInterface.ip = iptemp.ip
        newInterface.mask = iptemp.mask
        newInterface.gw = iptemp.gw
        newInterface.dns1 = iptemp.dns1
        newInterface.dns2 = iptemp.dns2
        #Relate the IPs created with the VMmodel
        try:
            VMmodel.setIPs()
        except Exception as e:
            print e
            raise e

        VMmodel.setMacs()
