from sqlalchemy import (Table, Column, MetaData, ForeignKey, PickleType, String,
                                                Integer, Text, create_engine, select, and_, or_, not_,
                                                event)
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import expression

import hashlib
import os.path
import datetime

from amsoil.config import (CONFIGDB_PATH, CONFIGDB_ENGINE)
from amsoil.core.exception import CoreException
from amsoil.core import serviceinterface
import amsoil.core.pluginmanager as pm

import amsoil.core.log
logger=amsoil.core.log.getLogger('configdb')

auth = pm.getService("authorization")

# initialize sqlalchemy
engine = create_engine(CONFIGDB_ENGINE, pool_recycle=6000)
metadata = MetaData(bind=engine)

tconfig = Table('config', metadata,
    Column('id', Integer, primary_key=True),
    Column('key', String(256)),
    Column('value', PickleType),
    Column('desc', Text),
    Column('rwattr', Integer),
    Column('roattr', Integer),
    Column('updatefunc', String(256))) # Called w/key and new value


class UnknownConfigKey(CoreException):
    def __init__ (self, key):
        super(UnknownConfigKey, self).__init__()
        self.key = key
    def __str__ (self):
        return "Unknown config key '%s'" % (self.key)

class UnknownConfigID(CoreException):
    def __init__ (self, cid):
        super(UnknownConfigID, self).__init__()
        self.cid = cid
    def __str__ (self):
        return "No config value with id %d" % (self.cid)

class UnknownUpdateFunc(CoreException):
    def __init__ (self, key, func):
        super(UnknownUpdateFunc, self).__init__()
        self.func = func
    def __str__ (self):
        return "Can't find update function (%s)" % (self.func)

class InvalidBooleanInput(CoreException):
    def __init__ (self, value):
        super(InvalidBooleanInput, self).__init__()
        self.val = value
    def __str__ (self):
        return "Don't know how to coerce value (%s) of type (%s) to boolean" % (
                        str(self.val), type(self.val))

class ConfigItem(object):
    def __init__ (self, row = None):
        if row is not None:
            self.id = row[tconfig.c.id]
            self.key = row[tconfig.c.key]
            self.desc = row[tconfig.c.desc]
            self.__value = row[tconfig.c.value]
            if row[tconfig.c.rwattr]:
                self.__rwattr = auth.AttrDB.getAttribute(row[tconfig.c.rwattr])
            if row[tconfig.c.roattr]:
                self.__roattr = auth.AttrDB.getAttribute(row[tconfig.c.roattr])
            self.updatefuncname = row[tconfig.c.updatefunc]
            try:
                self.__updatefunc = Config.resolveUpdateFunc(self.updatefuncname) # TODO this should be done with signaling, if the notification plugin can be loaded before this plugin
            except UnknownUpdateFunc, e:
                logger.warning("Couldn't find update function (%s) for key (%s)" % (e.func, self.key))
                self.__updatefunc = None
        else:
            self.key = None
            self.desc = None
            self.__value = None
            self.__rwattr = None
            self.__roattr = None
            self.__updatefunc = None
            self.updatefuncname = None

    def hasEquivalentDefinition (self, other):
        if ((self.key == other.key) and
             (self.desc == other.desc) and
             (self.updatefuncname == other.updatefuncname)):
            return True
        else:
            return False

    def updateDefinition (self, other):
        self.key = other.key
        self.desc = other.desc
        self.updatefuncname = other.updatefuncname
        self.__updatefunc = Config.resolveUpdateFunc(self.updatefuncname)
        Config.updateDefinition(self)

    @serviceinterface
    def setKey (self, key):
        self.key = key
        return self

    @serviceinterface
    def getRWAttrs (self):
        return self.__rwattr

    @serviceinterface
    def getROAttrs (self):
        return self.__roattrs

    @serviceinterface
    def write (self, value, user = None):
        if user:
            user.assertPrivilege(self.__rwattr)
        if self.__updatefunc:
            value = self.__updatefunc(self.key, value)
        self.setValue(value)
        Config.writeValue(self, value)
        
    @serviceinterface
    def setValue (self, value):
        self.__value = value
        return self

    @serviceinterface
    def setDesc (self, desc):
        self.desc = desc
        return self

    @serviceinterface
    def setUpdateFuncName (self, name):
        # TODO see other comments regarding changing this to signals
        self.updatefuncname = name
        return self

    @serviceinterface
    def getValue (self, user = None):
        if user:
            user.assertPrivilege((self.__rwattr, self.__roattr))
        return self.__value


class _DB(object):
    def __init__ (self):
        self._session = None

        self._updateFuncs = {None : self._writeThrough}
        self._cfgItemsByKey = {}
        self._cfgItemsByID = {}

        self._attributesByID = {}
        self._attributesByName = {}
        self._contextsByName = {}
        self._rolesByID = {}
        self._rolesByName = {}
        if not os.path.exists(CONFIGDB_PATH):
            self.__initDBCore()

        self.importing = False

    @property
    def session (self):
        if self._session == None:
            self._session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                                                                                    bind=engine, expire_on_commit=False))
        if not self._session.is_active:
            logger.warn("Rolling back inactive session")
            self._session.rollback()
        return self._session

    @session.deleter
    def session (self):
        self._session.remove()

    def close (self, sender, **extra):
        if self._session is not None:
            self._session.remove()
            self._session = None

    def connection (self):
        return self.session.connection()

    def commit (self):
        self.session.commit()
        
    def _writeThrough (self, key, newval):
        logger.debug("Writing item (%s) with value (%s)" % (key, str(newval)))
        return newval

    def __initDBCore (self):
        logger.info("No database found: initializing schema")
        metadata.drop_all()
        metadata.create_all()
    
    def initDB (self):
        self.__initDBCore()

    @serviceinterface
    def getConfigItem (self, key=None, cid=None):
        if key:
            return self._cfgItemsByKey.setdefault(key, self.loadConfigItem(key=key))
        elif cid:
            return self._cfgItemsByID.setdefault(cid, self.loadConfigItem(cid=cid))

    def writeValue (self, item, value):
        u = tconfig.update().where(tconfig.c.id==item.id).values(value=value)
        conn = self.connection()
        result = conn.execute(u)
        self.commit()

    def updateDefinition (self, item):
        u = tconfig.update().where(tconfig.c.id==item.id).values(
                    key=item.key, desc=item.desc, updatefunc=item.updatefuncname)
        conn = self.connection()
        result = conn.execute(u)
        self.commit()

    @serviceinterface
    def installConfigItem (self, item):
        try:
            oitem = self.getConfigItem(item.key)
            if item.hasEquivalentDefinition(oitem):
                return
            else:
                logger.info("updating definition of config item %s" % (item.key,))
                oitem.updateDefinition(item)
                return
        except UnknownConfigKey, e:
            logger.info("creating definition for config item %s" % (item.key,))
            self.createConfigItem(item)

    @serviceinterface
    def loadConfigItem (self, cid = None, key = None):
        conn = self.connection()
        if cid:
            s = select([tconfig], tconfig.c.id==cid)
        elif key:
            s = select([tconfig], tconfig.c.key==key)
        res = conn.execute(s)
        row = res.first()
        if row is None:
            if cid:
                raise UnknownConfigID(cid)
            elif key:
                raise UnknownConfigKey(key)
        item = ConfigItem(row)
        self._cfgItemsByID[item.id] = item
        self._cfgItemsByKey[item.key] = item
        return item
    
    @serviceinterface
    def loadAllConfigItems(self):
        conn = self.connection()
        s = select([tconfig])
        rs = conn.execute(s)
        resultList = []
        for row in rs:
            item = self.loadConfigItem(cid=row[tconfig.c.id])
            resultList.append(item)
        return resultList

    @serviceinterface
    def createConfigItem (self, item):
        logger.debug("Creating config item %s" % (item.key))
        conn = self.connection()
        ins = tconfig.insert().values(key=item.key, desc=item.desc, value=item.getValue(),
                                                                    updatefunc=item.updatefuncname)
        res = conn.execute(ins)
        self.commit()

    def resolveUpdateFunc (self, name):
        try:
            return self._updateFuncs[name]
        except KeyError, e:
            pass

        try:
            (mname, fname) = name.rsplit('.', 1) # TODO this should be done via signaling
            mod = importlib.import_module(mname)
            fobj = getattr(mod, fname)
            self._updateFuncs[name] = fobj
            logger.debug("Resolved update func %s" % (name))
            return fobj
        except AttributeError, e:
            logger.warning("Couldn't find update function %s in module %s" % (fname, mname))
        except ImportError, e:
            logger.warning("Couldn't find module %s for update function %s" % (mname, fname))
        except Exception, e:
            logger.exception("Import Exception", e)


### Standard type coercion utilities ###
def coerceBool (key, newval):
    if type(newval) is bool:
        return newval
    if newval.lower().strip() == "true":
        return True
    elif newval.lower().strip() == "false":
        return False
    raise InvalidBooleanInput(newval)


Config = _DB()
serviceinterface(Config)

@event.listens_for(engine, "before_execute")
def _log_execute (conn, clauseelement, multiparams, params):
    if isinstance(clauseelement, (expression.Insert, expression.Update, expression.Delete)):
        logger.debug("Lock %s" % (type(clauseelement)))

@event.listens_for(engine, "commit")
def _log_commit (conn):
    logger.debug("Unlock (commit)")

@event.listens_for(engine, "rollback")
def _log_rollback (conn):
    logger.debug("Unlock (rollback)")


