from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class VTServerMacRange(Base):
    """Please see the Database wiki page."""
    __tablename__ = 'vt_manager_vtserver_subscribedMacRanges'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = Column(Integer, nullable=False)
    macrange_id = Column(Integer, nullable=False)

