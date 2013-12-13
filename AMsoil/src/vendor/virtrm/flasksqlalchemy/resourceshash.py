from sqlalchemy import Column, Integer, String

from utils.commonbase import Base


'''@author: SergioVidiella'''


class ResourcesHash(Base):
    """Class to store resources hash"""

    __tablename__ = 'vt_manager_resourceshash'

    id = Column(Integer, autoincrement=True, primary_key=True)
    hashValue = Column(String(1024), nullable=False)
    projectUUID = Column(String(1024), nullable=False)
    sliceUUID = Column(String(1024), nullable=False)
