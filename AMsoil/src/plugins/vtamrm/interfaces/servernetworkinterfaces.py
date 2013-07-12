from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from utils.commonbase import Base


'''@author: SergioVidiella'''


class VTServerNetworkInterfaces(Base):
    """Network interfaces related to a VTServer."""

    __tablename__ = 'vt_manager_vtserver_networkInterfaces'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = Column(Integer, ForeignKey('vt_manager_vtserver.id')
    networkinterface_id = Column(Integer, ForeignKey('vt_manager_networkinterface')

    server = relationship("VTServer", backref=backref("vtserver_networkintefaces", cascade="all, delete-orphan"))
    networkinterface = relationship("NetworkInterface")


