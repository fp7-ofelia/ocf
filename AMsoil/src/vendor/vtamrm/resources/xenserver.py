from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE
from sqlalchemy.orm import validates, relationship, backref

from utils.commonbase import Base, DB_SESSION
from utils.choices import VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass
from utils.mutexstore import MutexStore

from resources.xenservervms import XenServerVMs
from resources.xenvm import XenVM
from resources.virtualmachine import VirtualMachine


'''@author: SergioVidiella'''


def validateAgentURLwrapper():
        VTServer.validateAgentURL()

class XenServer(Base):
    """Virtualization Server Class."""
        
    __tablename__ = 'vt_manager_xenserver'
    __table_args__ = {'extend_existing':True}

    vtserver_ptr_id = Column(Integer, ForeignKey('vt_manager_vtserver.id'), primary_key=True)

    '''VMs array'''
    vms = relationship("XenServerVMs")

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
            self.vtserver.setName(name)
            self.vtserver.setVirtTech(VirtTechClass.VIRT_TECH_TYPE_XEN)
            self.vtserver.setOSType(osType)
            self.vtserver.setOSDistribution(osDistribution)
            self.vtserver.setOSVersion(osVersion)
            self.vtserver.setAgentURL(agentUrl)
            self.vtserver.setAgentPassword(agentPassword)
            return self
	except Exception as e:
            print e
            self.destroy()
            raise e

    '''Updater'''
    def updateServer(self,name,osType,osDistribution,osVersion,agentUrl,agentPassword,save=True):
    	try:
            self.vtserver.setName(name)
            self.vtserver.setVirtTech(VirtTechClass.VIRT_TECH_TYPE_XEN)
            self.vtserver.setOSType(osType)
            self.vtserver.setOSDistribution(osDistribution)
            self.vtserver.setOSVersion(osVersion)
            self.vtserver.setAgentURL(agentUrl)
            self.vtserver.setAgentPassword(agentPassword)
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
            if len(DB_SESSION.query(VirtualMachine).filter(VirtualMachine.uuid == uuid).all()) > 0:
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

