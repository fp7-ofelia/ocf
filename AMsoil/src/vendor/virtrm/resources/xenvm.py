from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE
from sqlalchemy.orm import validates, relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

from utils.commonbase import Base, db_session
from utils.choices import HDSetupTypeClass, VirtTypeClass
from utils.mutexstore import MutexStore

from resources.virtualmachine import VirtualMachine

from interfaces.vmnetworkinterfaces import VMNetworkInterfaces

import amsoil.core.log

logging=amsoil.core.log.getLogger('XenVM')


'''@author: SergioVidiella'''


class XenVM(VirtualMachine):
    """XEN VM data model class"""

    __tablename__ = 'vt_manager_xenvm'
    __table_args__ = {'extend_existing':True}

    '''General Attributes'''
    virtualmachine_ptr_id = Column(Integer, ForeignKey('vt_manager_virtualmachine.id'), primary_key=True)
    hdSetupType = Column(String(1024), nullable=False, default="")
    hdOriginPath = Column(String(1024), nullable=False, default="")
    virtualizationSetupType = Column(String(1024), nullable=False, default="")

    vm = relationship("VirtualMachine", backref="xenvm")
    xenserver = association_proxy("xenserver_associations", "xenserver")

    @staticmethod
    def constructor(name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,interfaces,hdSetupType,hdOriginPath,virtSetupType,save=False):
        logging.debug("************************************* XENVM 2")
	self =  XenVM()
	try:
	    #Set common fields
            self.setName(name)
	    logging.debug("******************************** XENVM OK")
            self.setUUID(uuid)
            self.setProjectId(projectId)
	    self.setProjectName(projectName)
            self.setSliceId(sliceId)
            self.setSliceName(sliceName)
            self.setOSType(osType)
            self.setOSVersion(osVersion)
            self.setOSDistribution(osDist)
            self.setMemory(memory)
            self.setDiscSpaceGB(discSpaceGB)
            self.setNumberOfCPUs(numberOfCPUs)
            self.setCallBackURL(callBackUrl)
            self.setState(self.UNKNOWN_STATE)
            logging.debug("************************************* XENVM 3")
            #Xen parameters
            logging.debug("************************************* XENVM 5")
            self.hdSetupType = hdSetupType
            self.hdOriginPath = hdOriginPath
            self.virtualizationSetupType = virtSetupType
	    if save is True:
	        logging.debug("************************************* XENVM 6")
		db_session.add(self)
		db_session.commit()
            for interface in interfaces:
                logging.debug("************************************* XENVM 4")
		vm_iface = VMNetworkInterfaces()
		vm_iface.virtualmachine_id = self.id
		vm_iface.networkinterface_id = interface.id
                db_session.add(vm_iface)
		db_session.commit()
	except Exception as e:
            logging.debug("************************************* XENVM ERROR - 1 " + str(e))
            self.destroy()
            print e
            raise e
	return self

    '''Destructor'''
    def destroy(self):
    	with MutexStore.getObjectLock(self.getLockIdentifier()):
            #destroy interfaces
            for inter in self.networkInterfaces.all():
            	inter.destroy()
            db_session.delete(self)
	    db_session.commit()

    '''Validators'''
    @validates('hdSetupType')
    def validate_hd_setup_type(self, key, hd_setup_type):
	try:
	    HDSetupTypeClass.validate_hd_setup_type(hd_setup_type)
	    return hd_setup_type
	except Exception as e:
	    raise e

    @validates('virtualizationSetupType')
    def validate_virtualization_setup_type(self, key, virt_type):
	try:
	    VirtTypeClass.validate_virt_type(virt_type)
	    return virt_type
	except Exception as e:
	    raise e

    ''' Getters and setters '''
    def getHdSetupType(self):
        return  self.hdSetupType

    def setHdSetupType(self,hdType):
        HDSetupTypeClass.validate_hd_setup_type(hdType)
        self.hdSetupType = hdType

    def getHdOriginPath(self):
        return  self.hdSetupType

    def setHdOriginPath(self,path):
        self.hdOriginPath = path
        
    def getVirtualizationSetupType(self):
        return  self.virtualizationSetupType

    def setVirtualizationSetupType(self,vType):
        VirtTypeClass.validate_virt_type(vType)
        self.virtualizationSetupType = vType

    ''' Factories '''
    @staticmethod
    def create(name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,interfaces,hdSetupType,hdOriginPath,virtSetupType,save):
	logging.debug("************************************* XENVM 1")
    	return XenVM.constructor(name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,interfaces,hdSetupType,hdOriginPath,virtSetupType,save)

