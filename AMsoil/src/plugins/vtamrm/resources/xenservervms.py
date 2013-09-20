from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from utils.commonbase import Base


'''@author: SergioVidiella'''


class XenServerVMs(Base):
    """Relation between Xen Virtual Machines and Xen Virtualization Server"""

    __tablename__ = 'vt_manager_xenserver_vms'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    xenserver_id = Column(Integer, ForeignKey('vt_manager_xenserver.vtserver_ptr_id'))
    xenvm_id = Column(Integer, ForeignKey('vt_manager_xenvm.virtualmachine_ptr_id'))

    xenvm = relationship("XenVM", backref="xenserver_associations")


