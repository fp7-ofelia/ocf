from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime, timedelta

from utils.commonbase import Base


'''@author: SergioVidiella'''

class VMExpires(Base):
    """Expiration time of the Virtual Machine (only GeniV3)."""
    __tablename__ = 'amsoil_vt_manager_virtualmachine_expires'

    id = Column(Integer, autoincrement=True, primary_key=True)
    #XXX: should be a ForeignKey, this class should have the vms as an attribute?
    vm_id = Column(Integer, nullable=False)
    expires = Column(Date)
