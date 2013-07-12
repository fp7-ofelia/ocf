from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class VirtualMachine(Base):
    """Please see the Database wiki page."""
    __tablename__ = 'vt_manager_virtualmachine'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(512))
    uuid = Column(String(1024))
    memory = Column(Integer)
    numberOfCPUs = Column(Integer)
    discSpaceGB = Column(DOUBLE)
    projectId = Column(String(1024))
    projectName = Column(String(1024))
    sliceId = Column(String(1024))
    sliceName = Column(String(1024))
    guiUserName = Column(String(1024))
    guiUserUUID = Column(String(1024))
    expedientId = Column(Integer)
    operatingSystemType = Column(String(512))
    operatingSystemVersion = Column(String(512))
    operatingSystemDistribution = Column(String(512))
    callBackURL = Column(String(200))
    state = Column(String(24))
