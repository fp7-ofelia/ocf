from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from utils.commonbase import Base

'''@author: SergioVidiella'''


class VTServerMacRange(Base):
    """Subscribed Mac ranges to the VTServer's."""

    __tablename__ = 'vt_manager_vtserver_subscribedMacRanges'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = Column(Integer, ForeignKey('vt_manager_vtserver.id'))
    macrange_id = Column(Integer, ForeignKey('vt_manager_macrange.id'))

    vtserver = relationship("VTServer", backref="vtserver_mac_range", lazy="dynamic")
    subscribed_mac_range = relationship("MacRange", backref="vtserver_association")

