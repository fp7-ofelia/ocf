import os.path
from datetime import datetime

from sqlalchemy import Table, Column, MetaData, ForeignKey, PickleType, DateTime, String, Integer, Text, create_engine, select, and_, or_, not_, event
from sqlalchemy.orm import scoped_session, sessionmaker, mapper
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.declarative import declarative_base

import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('worker')

from amsoil.config import expand_amsoil_path

WORKERDB_PATH = expand_amsoil_path(pm.getService('config').get('worker.dbpath'))
WORKERDB_ENGINE = "sqlite:///%s" % (WORKERDB_PATH,)

# initialize sqlalchemy
db_engine = create_engine(WORKERDB_ENGINE, pool_recycle=6000) # please see the wiki for more info
db_session_factory = sessionmaker(autoflush=True, bind=db_engine, expire_on_commit=False) # the class which can create sessions (factory pattern)
db_session = scoped_session(db_session_factory) # still a session creator, but it will create _one_ session per thread and delegate all method calls to it
# we could limit the session's scope (lifetime) to one request, but for this plugin it is not necessary
Base = declarative_base() # get the base class for the ORM, which includes the metadata object (collection of table descriptions)

class JobDBEntry(Base):
    __tablename__ = 'worker_jobs'
    id = Column(Integer, primary_key=True)
    service_name = Column(String)
    callable_attr_str = Column(String)
    params = Column(PickleType)
    recurring_interval = Column(Integer)
    next_execution = Column(DateTime)

Base.metadata.create_all(db_engine) # create the tables if they are not there yet

def getAllJobs():
    """Do not change the values of the records retrieved with this function. You might accedently change them in the database too. Unless you call updateJob"""
    records = db_session.query(JobDBEntry).all()
    return records

def addJob(job_db_entry):
    """Creates a config item, if it does not exist. If it already exists this function does not change anything."""
    job_db_entry.id = None
    db_session.add(job_db_entry)
    db_session.commit()

def commit():
    """Commits the changes to objects in the session (e.g. a changed attribute in an object)."""
    db_session.commit()
    
def delJob(job_db_entry):
    db_session.delete(job_db_entry)
    db_session.commit()
