from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE
from sqlalchemy.orm import validates

from utils.commonbase import Base
from utils.choices import HDSetupTypeClass, VirtTypeClass
from utils.mutexstore import MutexStore


'''@author: SergioVidiella'''


class XenVM(Base):
    """XEN VM data model class"""

    __tablename__ = 'vt_manager_xenvm'
    __table_args__ = {'extend_existing':True}

    '''General Attributes'''
    virtualmachine_ptr_id = Column(Integer, ForeignKey('vt_manager_virtualmachine.id'), primary_key=True)
    hdSetupType = Column(String(1024), nullable=False, default="")
    hdOriginPath = Column(String(1024), nullable=False, default="")
    virtualizationSetupType = Column(String(1024), nullable=False, default="")

    @staticmethod
    def constructor(name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,interfaces,hdSetupType,hdOriginPath,virtSetupType):
       self =  XenVM()
            try:
            	#Set common fields
                self.vm.setName(name)
                self.vm.setUUID(uuid)
                self.vm.setProjectId(projectId)
		self.vm.setProjectName(projectName)
                self.vm.setSliceId(sliceId)
                self.vm.setSliceName(sliceName)
                self.vm.setOSType(osType)
                self.vm.setOSVersion(osVersion)
                self.vm.setOSDistribution(osDist)
                self.vm.setMemory(memory)
                self.vm.setDiscSpaceGB(discSpaceGB)
                self.vm.setNumberOfCPUs(numberOfCPUs)
                self.vm.setCallBackURL(callBackUrl)
                self.vm.setState(self.UNKNOWN_STATE)
                for interface in interfaces:
                    self.vm.networkInterfaces.add(interface)
                #Xen parameters
                self.hdSetupType = hdSetupType
                self.hdOriginPath = hdOriginPath
                self.virtualizationSetupType = virtSetupType
	    except Exception as e:
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
            self.delete()

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
    def create(name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,interfaces,hdSetupType,hdOriginPath,virtSetupType):
    	return XenVM.constructor(name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,interfaces,hdSetupType,hdOriginPath,virtSetupType,save)

