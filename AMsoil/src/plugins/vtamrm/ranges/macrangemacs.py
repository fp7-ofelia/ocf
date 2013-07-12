from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from utils.commonbase import Base

'''@author: svidiella'''

class MacRangeMacs(Base):
    """Relation between Mac's and MacRange"""

    __tablename__ = 'vt_manager_macrange_macs'
   
    id = Column(Integer, autoincrement=True, nullable=False,primary_key=True)
    macslot_id = Column(Integer, ForeignKey('vt_manager_macslot.id'))
    macrange_id = Column(Integer, ForeignKey('vt_manager_macrange.id'))

    macrange = relationship("MacRange", backref=backref("mac_macrange", cascade="all, delete-orphan"))
    macslot = relationshitp("MacSlot", backref=backref("macrange_macs"))

