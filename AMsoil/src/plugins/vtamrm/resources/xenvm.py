from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

from resources.virtualmachine import VirtualMachine

from utils.choices import HDSetupTypeClass, VirtTypeClass
from utils.mutexstore import MutexStore


'''@author: SergioVidiella'''


class XenVM(VirtualMachine):
    """XEN VM data model class"""

    __tablename__ = 'vt_manager_xenvm'

    '''General Attributes'''
    server = association_proxy('vm_server', 'server')
    hdSetupType = Column(String(1024), nullable=False, default="")
    hdOriginPath = Column(String(1024), nullable=False, default="")
    virtualizationSetupType = Column(String(1024), nullable=False, default="")

    @staticmethod
    def constructor(name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,interfaces,hdSetupType,hdOriginPath,virtSetupType):
       self =  XenVM()
            try:
            	#Set common fields
                self.setName(name)
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
                for interface in interfaces:
                    self.networkInterfaces.add(interface)
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

