from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import DateTime, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

import amsoil.core.pluginmanager as pm


'''@author: SergioVidiella'''

Base = declarative_base()

config = pm.getService("config")
ENGINE = "%s://%s:%s@%s/%s" % (
								config.get("virtrm.DATABASE_ENGINE"), config.get("virtrm.DATABASE_USER"),
								config.get("virtrm.DATABASE_PASSWORD"), config.get("virtrm.DATABASE_HOST"),
								config.get("virtrm.DATABASE_NAME"),
								)
db_engine = create_engine(ENGINE, pool_recycle=6000)
# Class that can create sessions (factory pattern)
db_session_factory = sessionmaker(autoflush=True, bind=db_engine, expire_on_commit=False)
# Still a session generator, but it will create _one_ session per thread and delegate all method calls to it
db_session = scoped_session(db_session_factory)

