from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from utils.commonbase import Base

'''@author: SergioVidiella'''


class VTServerIpRange(Base):
    """Subscribed Mac ranges to the VTServer's."""

    __tablename__ = 'vt_manager_vtserver_subscribedMacRanges'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = Column(Integer, ForeignKey('vt_manager_vtserver.id'))
    macrange_id = Column(Integer, ForeignKey('vt_manager_macrange.id'))

    server = relationship("VTServer", backref=backref("vtserver_subscribed_macranges", cascade="all, delete-orphan"))
    subscribedMacRange = relationship("MacRange")

