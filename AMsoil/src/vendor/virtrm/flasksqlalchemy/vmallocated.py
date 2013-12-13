from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import validates, relationship

from datetime import datetime, timedelta

from utils.commonbase import Base
from utils.choices import HDSetupTypeClass, VirtTypeClass, VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass
from utils.mutexstore import MutexStore
from utils import validators


'''@author: SergioVidiella'''


class VMAllocated(Base):
    """Virtual Machines allocated for GeniV3 calls."""

    __tablename__ = 'amsoil_vt_manager_virtualmachine_allocated'

    '''General parameters'''
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(512), nullable=False, default="")
    memory = Column(Integer)
    numberOfCPUs = Column(Integer)
    discSpaceGB = Column(DOUBLE)

    '''Property parameters'''
    projectName = Column(String(1024), nullable=False, default="")
    sliceId = Column(String(1024), nullable=False, default="")
    sliceName = Column(String(512), nullable=False, default="")
    serverId = Column(Integer)

    '''OS parameters'''
    operatingSystemType = Column(String(512), nullable=False, default="")
    operatingSystemVersion = Column(String(512), nullable=False, default="")
    operatingSystemDistribution = Column(String(512), nullable=False, default="")

    '''Virtualization parameteres'''
    virtualizationSetupType = Column(String(1024), nullable=False, default="")
    hdSetupType = Column(String(1024), nullable=False, default="")
    hdOriginPath = Column(String(1024), nullable=False, default="")
    hypervisor = Column(String(512), nullable=False, default="xen")

    '''Allocation expiration time'''
    expires = Column(Date, nullable=False) 


    @staticmethod
    def constructor(name,projectId,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,hdSetupType,hdOriginPath,virtSetupType,hypervisor, expires):
	self = VMAllocated()
	try:
	    self.name = name 
	    self.projectId = projectId
	    self.sliceId = sliceId
	    self.sliceName = sliceName
	    self.operatingSystemType = osType
	    self.operatingSystemVersion = osVersion
	    self.operatingSystemDistribution = osDist
	    self.memory = memory
	    self.discSpaceGB = discSpaceGB
	    self.numberOfCPUs = numberOfCPUs
	    self.hdSetupType = hdSetupType
	    self.hdOriginPath = hdOriginPath
	    self.virtualizationSetupType = virtSetupType
	    self.hypervisor = hypervisor
	    self.expires = expires
	except Exception as e:
	    self.destroy()
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

    @validates('name')
    def validate_name(self, key, name):
        try:
            validators.vm_name_validator(name)
            return name
        except Exception as e:
            raise e

    @validates('operatingSystemType')
    def validate_operatingsystemtype(self, key, os_type):
        try:
            OSTypeClass.validateOSType(os_type)
            return os_type
        except Exception as e:
            raise e

    @validates('operatingSystemDistribution')
    def validate_operatingsystemdistribution(self, key, os_distribution):
        try:
            OSDistClass.validateOSDist(os_distribution)
            return os_distribution
        except Exception as e:
            raise e

    @validates('operatingSystemVersion')
    def validate_operatingsystemversion(self, key, os_version):
        try:
            OSVersionClass.validateOSVersion(os_version)
            return os_version
        except Exception as e:
            raise e


