from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import DateTime, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

import amsoil.core.pluginmanager as pm


'''@author: SergioVidiella'''


Base = declarative_base()

config = pm.getService("config")
ENGINE = config.get("vtamrm.DATABASE_ENGINE")+"://"+config.get("vtamrm.DATABASE_USER")+":"+config.get("vtamrm.DATABASE_PASSWORD")+"@"+config.get("vtamrm.DATABASE_HOST")+"/"+config.get("vtamrm.DATABASE_NAME")
db_engine = create_engine(ENGINE, pool_recycle=6000)
db_session_factory = sessionmaker(autoflush=True, bind=db_engine, expire_on_commit=False) # the class which can create sessions (factory pattern)
db_session = scoped_session(db_session_factory) # still a session creator, but it will create _one_ session per thread and delegate all method calls to it

