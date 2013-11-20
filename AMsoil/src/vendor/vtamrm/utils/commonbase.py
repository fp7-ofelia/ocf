from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import DateTime, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound


'''@author: SergioVidiella'''


Base = declarative_base()

#Generate this from settings!
ENGINE = "mysql://root:ofelia4you@localhost/vt_am879544567"
db_engine = create_engine(ENGINE, pool_recycle=6000)
db_session_factory = sessionmaker(autoflush=True, bind=db_engine, expire_on_commit=False) # the class which can create sessions (factory pattern)
DB_SESSION = scoped_session(db_session_factory) # still a session creator, but it will create _one_ session per thread and delegate all method calls to it

