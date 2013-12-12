from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE
from sqlalchemy.orm import validates, relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

from utils.commonbase import Base, db_session
from utils.choices import VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass
from utils.mutexstore import MutexStore

from resources.xenservervms import XenServerVMs
from resources.xenvm import XenVM
from resources.virtualmachine import VirtualMachine
from resources.vtserver import VTServer


import amsoil.core.log

logging=amsoil.core.log.getLogger('XenServer')


'''@author: SergioVidiella'''


def validateAgentURLwrapper():
        VTServer.validateAgentURL()

class XenServer(VTServer):
    """Virtualization Server Class."""
        
    __tablename__ = 'vt_manager_xenserver'
    __table_args__ = {'extend_existing':True}

    vtserver_ptr_id = Column(Integer, ForeignKey('vt_manager_vtserver.id'), primary_key=True)
    vtserver = relationship("VTServer", backref="xenserver")

    '''VMs array'''
    vms = association_proxy("xenserver_vms", "xenvm")

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
	    db_session.add(self)
	    db_session.commit()
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
	    db_session.add(self)
	    db_session.commit()
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

    def createVM(self, name, uuid, projectId, projectName, sliceId, sliceName, osType, osVersion, osDist, memory, discSpaceGB, numberOfCPUs, callBackUrl, hdSetupType, hdOriginPath, virtSetupType,save):
	logging.debug("**************************** Server 1")
	with MutexStore.getObjectLock(self.getLockIdentifier()):
	    logging.debug("******************************* Server 2")
            if len(db_session.query(VirtualMachine).filter(VirtualMachine.uuid == uuid).all()) > 0:
		logging.debug("*************************** Server FAIL")
    		raise Exception("Cannot create a Virtual Machine with the same UUID as an existing one")
            #Allocate interfaces for the VM
	    logging.debug("*************************** Server 3")
            interfaces = self.createEnslavedVMInterfaces()
            #Call factory	
	    logging.debug("**************************** Server 4")
            vm = XenVM.create(name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,interfaces,hdSetupType,hdOriginPath,virtSetupType,save=True)
	    logging.debug("**************************** Server 5")
            xen_vms = XenServerVMs()
	    xen_vms.xenserver_id = self.id
	    xen_vms.xenvm_id = vm.id
	    db_session.add(xen_vms)
	    db_session.commit() 
	    logging.debug("**************************** Server 6")
            return vm

    def deleteVM(self,vm):
    	with MutexStore.getObjectLock(self.getLockIdentifier()):
            if vm not in self.vms.all():
            	raise Exception("Cannot delete a VM from pool if it is not already in")
            db_session.delete(vm)
	    db_session.commit()
            vm.destroy()

