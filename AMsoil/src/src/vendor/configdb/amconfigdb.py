from sqlalchemy import (Table, Column, MetaData, ForeignKey, PickleType, String,
                                                Integer, Text, create_engine, select, and_, or_, not_,
                                                event)
from sqlalchemy.orm import scoped_session, sessionmaker, mapper
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.declarative import declarative_base

from amsoil.config import (CONFIGDB_PATH, CONFIGDB_ENGINE)
from amconfigdbexceptions import ConfigDuplicateConfigKey, ConfigUnknownConfigKey
from amsoil.core import serviceinterface
import amsoil.core.pluginmanager as pm

import amsoil.core.log
logger=amsoil.core.log.getLogger('configdb')

# initialize sqlalchemy
db_engine = create_engine(CONFIGDB_ENGINE, pool_recycle=6000) # please see the wiki for more info
db_session_factory = sessionmaker(autoflush=True, bind=db_engine, expire_on_commit=False) # the class which can create sessions (factory pattern)
db_session = scoped_session(db_session_factory) # still a session creator, but it will create _one_ session per thread and delegate all method calls to it
# we could limit the session's scope (lifetime) to one request, but for this plugin this is not necessary
Base = declarative_base() # get the base class for the ORM, which includes the metadata object (collection of table descriptions)

class ConfigEntry(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(PickleType)
    desc = Column(Text)

Base.metadata.create_all(db_engine) # create the tables if they are not there yet

class ConfigDB:
    def _getRow(self, key):
        try:
            return db_session.query(ConfigEntry).filter_by(key=key).one()
        except MultipleResultsFound:
            raise ConfigDuplicateConfigKey(key)
        except NoResultFound:
            raise ConfigUnknownConfigKey(key)
        
    
    @serviceinterface
    def install(self, key, defaultValue, defaultDescription, force=False):
        """
        Creates a config item, if it does not exist. If it already exists and
        force is False this function does not change anything. If force is True,
        the exist item will be change.
        Return True if this function change the database, else False.
        """
        try:
            self._getRow(key)
        except ConfigUnknownConfigKey:
            record = ConfigEntry(key=key, value=defaultValue, desc=defaultDescription)
            db_session.add(record)
            db_session.commit()
        else:
            if(force):
                self.set(key, defaultValue)
            else:
                return False
        return True
    
    @serviceinterface
    def set(self, key, value):
        res = self._getRow(key)
        res.value = value
        db_session.commit()
    
    @serviceinterface
    def get(self, key):
        return self._getRow(key).value

    @serviceinterface
    def getAll(self):
        """
        Lists all config items available in the database.
        Returns a list of hashes. Each hash has the following keys set: key, value, description."""
        records = db_session.query(ConfigEntry).all()
        return [{'key':r.key, 'value':r.value, 'description':r.desc} for r in records]

# For Nick's old code, see old import2012 branch