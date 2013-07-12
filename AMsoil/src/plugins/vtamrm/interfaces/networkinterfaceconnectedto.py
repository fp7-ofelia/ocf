from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from utils.commonbase import Base

'''@author: svidiella'''

class NetworkInterfaceConnectedTo(Base):
    """Connections between Network interfaces"""

    __tablename__ = 'vt_manager_networkinterface_connectedTo'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    from_networkinterface_id = Column(Integer, ForeignKey('vt_manager_networkinterface.id'))
    to_networkinterface_id = Column(Integer, ForeignKey('vt_manager_networkinterface.id'))

    to_networkinterface = relationship("NetworkInterface", backref=backref("to_networkinterface")

