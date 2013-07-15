from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from utils.commonbase import Base


'''@author: SergioVidiella'''


class VMNetworkInterfaces(Base):
    """Network interfaces related to a Virtual Machine"""

    __tablename__ = 'vt_manager_virtualmachine_networkInterfaces'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    virtualmachine_id = Column(Integer, ForeignKey('vt_manager_virtualmachine.id'))
    networkinterface_id = Column(Integer, ForeignKey('vt_manager_networkinterface.id'))

    server = relationship("VirtualMachine", backref=backref("virtualmachine_networkintefaces", cascade="all, delete-orphan"))
    networkinterface = relationship("NetworkInterface")

