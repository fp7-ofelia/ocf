from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime, timedelta

Base = declarative_base()

class VMExpires(Base):
    """Please see the Database wiki page."""
    __tablename__ = 'vt_manager_virtualmachine_expires'

    id = Column(Integer, autoincrement=True, primary_key=True)
    vm_id = Column(Integer)
    expires = Column(Date)
