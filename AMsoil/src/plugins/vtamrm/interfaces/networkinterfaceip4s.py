from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from utils.commonbase import Base


'''@author: SergioVidiella'''


class NetworkInterfaceIp4s(Base):
    """Relation between Network interfaces and Ip's"""

    __tablename__ = 'vt_manager_networkinterface_ip4s'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    networkinterface_id = Column(Integer, ForeignKey('vt_manager_networkinterface.id'))
    ip4slot_id = Column(Integer, ForeignKey('vt_manager_networkinterface.id'))

    networkinterface = relationship("NetworkInterface", backref=backref("networkinterface_ip4s"))
    ip4slot = relationshitp("Ip4Slot", backref=backref("ip4_networkinterface"))

