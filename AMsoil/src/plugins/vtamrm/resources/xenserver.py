from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

from resources.vtserver import VTServer

from utils.choices import VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass
from utils.mutexstore import MutexStore


'''@author: SergioVidiella'''


def validateAgentURLwrapper():
        VTServer.validateAgentURL()

class XenServer(VTServer):
    """Virtualization Server Class."""
        
    __tablename__ = 'vt_manager_xenserver'

    vtserver_ptr_id = Column(Integer, primary_key=True)

    ''' VMs array '''
    vms = association_proxy('xenserver_xenvms', 'xenvm')

    '''Private methods'''
    def __tupleContainsKey(tu,key):
    	for val in tu:
            if val[0] == key:
            	return True
            return False

    def __addInterface(self,interface):
        if not isinstance(interface,NetworkInterface):
            raise Exception("Cannot add an interface if is not a NetworkInterface object instance")

    '''Constructors'''
    @staticmethod
    def constructor(name, osType, osDistribution, osVersion, agentUrl, agentPassword):
    	self = XenServer()
        try:
            self.setName(name)
            self.setVirtTech(VirtTechClass.VIRT_TECH_TYPE_XEN)
            self.setOSType(osType)
            self.setOSDistribution(osDistribution)
            self.setOSVersion(osVersion)
            self.setAgentURL(agentUrl)
            self.setAgentPassword(agentPassword)
            return self
	except Exception as e:
            print e
            self.destroy()
            raise e

    '''Updater'''
    def updateServer(self,name,osType,osDistribution,osVersion,agentUrl,agentPassword,save=True):
    	try:
            self.setName(name)
            self.setVirtTech(VirtTechClass.VIRT_TECH_TYPE_XEN)
            self.setOSType(osType)
            self.setOSDistribution(osDistribution)
            self.setOSVersion(osVersion)
            self.setAgentURL(agentUrl)
            self.setAgentPassword(agentPassword)
   	    return self
   	except Exception as e:
            print e
            self.destroy()
            raise e

    '''Destructor'''
    def destroy(self):
    	with MutexStore.getObjectLock(self.getLockIdentifier()):
            #destroy interfaces
            for inter in self.networkInterfaces.all():
            	inter.destroy()
                self.delete()

    ''' Public interface methods '''
    def getVMs(self,**kwargs):
        return self.vms.filter(**kwargs)
        
    def getVM(self,**kwargs):
        return self.vms.get(kwargs)

    def createVM(self, name, uuid, projectId, projectName, sliceId, sliceName, osType, osVersion, osDist, memory, discSpaceGB, numberOfCPUs, callBackUrl, hdSetupType, hdOriginPath, virtSetupType):
	with MutexStore.getObjectLock(self.getLockIdentifier()):
            if XenVM.objects.filter(uuid=uuid).count() > 0:
    		raise Exception("Cannot create a Virtual Machine with the same UUID as an existing one")
            #Allocate interfaces for the VM
            interfaces = self.createEnslavedVMInterfaces()
            #Call factory
            vm = XenVM.create(name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,interfaces,hdSetupType,hdOriginPath,virtSetupType)
            self.vms.add(vm)
            return vm

    def deleteVM(self,vm):
    	with MutexStore.getObjectLock(self.getLockIdentifier()):
            if vm not in self.vms.all():
            	raise Exception("Cannot delete a VM from pool if it is not already in")
            self.vms.remove(vm)
            vm.destroy()

