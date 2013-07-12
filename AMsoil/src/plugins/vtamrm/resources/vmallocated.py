from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime, timedelta

Base = declarative_base()

class VMAllocated(Base):
    """Please see the Database wiki page."""
    __tablename__ = 'vt_manager_virtualmachine_allocated'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(512))
    projectId = Column(String(1024))
    sliceId = Column(String(1024))
    sliceName = Column(String(512))
    serverId = Column(Integer)
    operatingSystemType = Column(String(512))
    operatingSystemVersion = Column(String(512))
    operatingSystemDistribution = Column(String(512))
    virtualizationSetupType = Column(String(1024))
    hdSetupType = Column(String(1024))
    hdOriginPath = Column(String(1024))
    hypervisor = Column(String(512))
    expires = Column(Date)  
