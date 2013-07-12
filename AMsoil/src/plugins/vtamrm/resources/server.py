from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class VTServer(Base):
    """Please see the Database wiki page."""
    __tablename__ = 'vt_manager_vtserver'

    id = Column(Integer, autoincrement=True, primary_key=True)
    available = Column(TINYINT(1))
    enabled = Column(TINYINT(1))
    name = Column(String(511))
    uuid = Column(String(1024))
    operatingSystemType = Column(String(512))
    operatingSystemDistribution = Column(String(512))
    operatingSystemVersion = Column(String(512))
    virtTech = Column(String(512))
    numberOfCPUs = Column(Integer)
    CPUFrequency = Column(Integer)
    memory = Column(Integer)
    discSpaceGB = Column(DOUBLE)
    agentURL = Column(String(200))
    agentPassword = Column(String(128))
    url = Column(String(200))

