from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class VTServerIpRange(Base):
    """Please see the Database wiki page."""
    __tablename__ = 'vt_manager_vtserver_subscribedIp4Ranges'
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = Column(Integer, nullable=False)
    ip4range_id = Column(Integer, nullable=False)

