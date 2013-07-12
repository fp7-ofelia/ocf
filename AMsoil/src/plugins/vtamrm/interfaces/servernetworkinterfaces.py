from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class VTServerNetworkInterfaces(Base):
    """Please see the Database wiki page."""
    __tablename__ = 'vt_manager_vtserver_networkInterfaces'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = Column(Integer, nullable=False)
    networkinterface_id = Column(Integer, nullable=False)

