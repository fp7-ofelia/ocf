# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University
# Copyright (c) 2012 Barnstormer Softworks

from sqlalchemy import (Table, Column, MetaData, ForeignKey, PickleType, String,
                        Integer, Text, create_engine, select, and_, or_, not_,
                        event)
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import expression

import hashlib
import logging
import os.path
import datetime

try:
  import importlib
except ImportError:
  import foamext.importlib as importlib

from foam.config import (CONFIGDB_PATH, CONFIGDB_ENGINE, GENICERTDIR)
from foam.core.log import KeyAdapter
from foam.core.exception import CoreException
from foam.core import auth

engine = create_engine(CONFIGDB_ENGINE, pool_recycle=6000)
metadata = MetaData(bind=engine)

tconfig = Table('config', metadata,
  Column('id', Integer, primary_key=True),
  Column('key', String(256)),
  Column('value', PickleType),
  Column('desc', Text),
  Column('rwattr', Integer, ForeignKey('attributes.id')),
  Column('roattr', Integer, ForeignKey('attributes.id')),
  Column('updatefunc', String(256))) # Called w/key and new value

tattributes = Table('attributes', metadata,
  Column('id', Integer, primary_key=True),
  Column('name', String(256)),
  Column('desc', Text))

troles = Table('roles', metadata,
  Column('id', Integer, primary_key=True),
  Column('name', String(256)),
  Column('desc', Text))

tusers = Table('users', metadata,
  Column('id', Integer, primary_key=True),
  Column('username', String(64)),
  Column('passwd', String(64)),
  Column('email', String(128)))

jRoleAttributes = Table('j_role_attributes', metadata,
  Column('role_id', Integer, ForeignKey('roles.id')),
  Column('attribute_id', Integer, ForeignKey('attributes.id')))

jUserRoles = Table('j_user_roles', metadata,
  Column('user_id', Integer, ForeignKey('users.id')),
  Column('role_id', Integer, ForeignKey('roles.id')))
  
jUserAttrs = Table('j_user_attributes', metadata,
  Column('user_id', Integer, ForeignKey('users.id')),
  Column('attribute_id', Integer, ForeignKey('attributes.id')))

class UnknownAttributeName(CoreException):
  def __init__ (self, name):
    super(UnknownAttributeName, self).__init__()
    self.name = name
  def __str__ (self):
    return "Attempted to reference unknown attribute '%s'" % (self.name)

class UnknownAttributeID(CoreException):
  def __init__ (self, aid):
    super(UnknownAttributeID, self).__init__()
    self.aid = aid 
  def __str__ (self):
    return "Attempted to reference unknown attribute with ID %d" % (self.aid)

class UnknownUser(CoreException):
  def __init__ (self, name):
    super(UnknownUser, self).__init__()
    self.name = name
  def __str__ (self):
    return "Attempted to reference unknown user '%s'" % (self.name)

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
      self.__rwattr = ConfigDB.getAttributeByID(row[tconfig.c.rwattr])
      self.__roattr = ConfigDB.getAttributeByID(row[tconfig.c.roattr])
      self.updatefuncname = row[tconfig.c.updatefunc]
      try:
        self.__updatefunc = ConfigDB.resolveUpdateFunc(self.updatefuncname)
      except UnknownUpdateFunc, e:
        ConfigDB.log.warning("Couldn't find update function (%s) for key (%s)" % (e.func, self.key))
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
    self.key == other.key
    self.desc == other.desc
    self.updatefuncname == other.updatefuncname
    self.__updatefunc = ConfigDB.resolveUpdateFunc(self.updatefuncname)
    ConfigDB.updateDefinition(self)

  def setKey (self, key):
    self.key = key
    return self

  def getRWAttrs (self):
    return self.__rwattr

  def getROAttrs (self):
    return self.__roattrs

  def write (self, value, user = None):
    if user:
      user.assertPrivilege(self.__rwattr)
    if self.__updatefunc:
      value = self.__updatefunc(self.key, value)
    self.setValue(value)
    ConfigDB.writeValue(self, value)
    
  def setValue (self, value):
    self.__value = value
    return self

  def setDesc (self, desc):
    self.desc = desc
    return self

  def setUpdateFuncName (self, name):
    self.updatefuncname = name
    return self

  def getValue (self, user = None):
    if user:
      user.assertPrivilege((self.__rwattr, self.__roattr))
    return self.__value


class _DB(object):
  def __init__ (self):
    self._session = None
    self.log = KeyAdapter("ConfigDB", logging.getLogger("foam"))

    self._updateFuncs = {None : self._writeThrough}
    self._cfgItemsByKey = {}
    self._cfgItemsByID = {}

    self._attributesByID = {}
    self._attributesByName = {}
    self._usersByID = {}
    self._usersByName = {}
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
      self.log.warn("Rolling back inactive session")
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
    self.log.debug("Writing item (%s) with value (%s)" % (key, str(newval)))
    return newval

  def __initDBCore (self):
    self.log.info("No database found: initializing schema")
    metadata.drop_all()
    metadata.create_all()
    self.__addDefaultVars()
  
  def __addDefaultVars (self):
    try:
      import socket
      site_tag = None
      site_tag = socket.getfqdn()
    except Exception:
      pass
      
    citems = []
    citems.append(ConfigItem().setKey("geni.max-lease").setValue(datetime.timedelta(weeks=2))
                  .setDesc("Max sliver lease time")
                  .setUpdateFuncName("foam.geni.lib.updateMaxLease"))
    citems.append(ConfigItem().setKey("geni.cert-dir").setValue(GENICERTDIR)
                  .setDesc("Directory for trusted SLL root certificates."))
    citems.append(ConfigItem().setKey("geni.site-tag").setValue(site_tag)
                  .setDesc("Site tag for GENI aggregates (used in URNs)")
                  .setUpdateFuncName("foam.geni.lib.siteTagChange"))

    citems.append(ConfigItem().setKey("geni.approval.approve-on-creation").setValue(0)
                  .setDesc("Approve slivers on creation.")
                  .setUpdateFuncName("foam.geni.approval.setMode"))
    citems.append(ConfigItem().setKey("geni.openflow.analysis-engine").setValue(True)
                  .setDesc("Run analysis engine for openflow slivers")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))

    citems.append(ConfigItem().setKey("geni.openflow.portgroups").setValue(None)
                  .setDesc("Internal Portgroups Storage")
                  .setUpdateFuncName("foam.geni.approval.updatePortGroups"))
    citems.append(ConfigItem().setKey("geni.approval.user-urns").setValue(None)
                  .setDesc("Internal User URN Storage")
                  .setUpdateFuncName("foam.geni.approval.updateUserURNs"))

    citems.append(ConfigItem().setKey("email.admin-addr").setValue(None)
                  .setDesc(""))
    citems.append(ConfigItem().setKey("email.smtp-server").setValue(None)
                  .setDesc(""))
    citems.append(ConfigItem().setKey("email.reply-to").setValue(None)
                  .setDesc(""))
    citems.append(ConfigItem().setKey("email.from").setValue(None)
                  .setDesc(""))
    citems.append(ConfigItem().setKey("email.event.createsliver.admin").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.disablesliver.admin").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.rejectsliver.admin").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.json-deletesliver.admin").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.gapi-deletesliver.admin").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.renewsliver.admin").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.approvesliver.admin").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.expiresliver.admin").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.expiresliverday.admin").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.expiresliverweek.admin").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.shutdownsliver.admin").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.pendingqueue.admin").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.createsliver.exp").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.disablesliver.exp").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.rejectsliver.exp").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.json-deletesliver.exp").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.gapi-deletesliver.exp").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.renewsliver.exp").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.approvesliver.exp").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.expiresliver.exp").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.expiresliverday.exp").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.expiresliverweek.exp").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))
    citems.append(ConfigItem().setKey("email.event.shutdownsliver.exp").setValue(True)
                  .setDesc("")
                  .setUpdateFuncName("foam.core.configdb.coerceBool"))

    citems.append(ConfigItem().setKey("site.admin.name").setValue(None)
                  .setDesc(""))
    citems.append(ConfigItem().setKey("site.admin.email").setValue(None)
                  .setDesc(""))
    citems.append(ConfigItem().setKey("site.admin.phone").setValue(None)
                  .setDesc(""))
    citems.append(ConfigItem().setKey("site.location.address").setValue(None)
                  .setDesc(""))
    citems.append(ConfigItem().setKey("site.location.organization").setValue(None)
                  .setDesc(""))
    citems.append(ConfigItem().setKey("site.description").setValue(None)
                  .setDesc(""))

    citems.append(ConfigItem().setKey("site.attachments").setValue({})
                  .setDesc("")
                  .setUpdateFuncName("foam.geni.peerdb.updateAttachments"))

#    citems.append(ConfigItem().setKey().setValue(None)
#                  .setDesc(""))
    [self.createConfigItem(x) for x in citems]

  def initDB (self):
    self.__initDBCore()
    # Call init_config_db for all plugins

  def getConfigItemByID (self, cid):
    return self._cfgItemsByID.setdefault(cid, self.loadConfigItem(cid=cid))

  def getConfigItemByKey (self, key):
    return self._cfgItemsByKey.setdefault(key, self.loadConfigItem(key=key))

  def writeValue (self, item, value):
    u = tconfig.update().where(tconfig.c.id==item.id).values(value=value)
    conn = self.connection()
    result = conn.execute(u)
    self.commit()

  def updateDefinition (self, item):
    u = tconfig.update().where(tconfig.c.id==item.id).values(
          key=self.key, desc=item.desc, updatefunc=item.updatefunc)
    conn = self.connection()
    result = conn.execute(u)
    self.commit()

  def installConfigItem (self, item):
    try:
      oitem = self.getConfigItemByKey(item.key)
      if item.hasEquivalentDefinition(oitem):
        return
      else:
        oitem.updateDefinition(item)
        return
    except UnknownConfigKey, e:
      self.createConfigItem(item)

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

  def createConfigItem (self, item):
    self.log.debug("Creating config item %s" % (item.key))
    conn = self.connection()
    ins = tconfig.insert().values(key=item.key, desc=item.desc, value=item.getValue(),
                                  updatefunc=item.updatefuncname)
    res = conn.execute(ins)
    self.commit()

  def getUser (self, uname):
    try:
      return self._usersByName[uname]
    except KeyError, e:
      pass

    if uname == "foamadmin":
      u = auth.SuperUser()
      u.id = -1
      u.name = "foamadmin"
    else:
      conn = self.connection()
      s = select([tusers], tusers.c.username==uname)
      res = conn.execute(s)
      row = res.first()
      if row is None:
        raise UnknownUser(uname)

      u = auth.User()
      u.id = row[tusers.c.id]
      u.name = row[tusers.c.username]
      u.email = row[tusers.c.email]

    self._usersByID[u.id] = u
    self._usersByName[u.name] = u

    return u

  def addUser (self, uname, passwd, email):
    conn = self.connection()
    passwd = hashlib.md5(passwd).hexdigest()
    ins = tusers.insert().values(username=uname, passwd=passwd, email=email)
    conn.execute(ins)
    self.commit()

  def getUserAttributes (self, uid):
    attrs = set()

    conn = self.connection()
    s = select([jUserAttrs], jUserAttrs.c.user_id==uid)
    res = conn.execute(s)
    for row in res:
      try:
        attrs.add(self._attributesByID[row[jUserAttrs.c.attribute_id]])
      except KeyError:
        attr = self.getAttrByID(row[jUserAttrs.c.attribute_id])
        attrs.add(attr)
    return attrs

  def setUserAttribute (self, uid, aid):
    conn = self.connection()
    ins = jUserAttrs.insert().values(user_id=uid, attribute_id=aid)
    conn.execute(ins)
    self.commit()

  def getAttributeByName (self, name):
    try:
      return self._attributesByName[name]
    except KeyError:
      pass

    conn = self.connection()
    s = select([tattributes], tattributes.c.name==name)
    res = conn.execute(s)
    row = res.first()
    if row is None:
      raise UnknownAttributeName(name)

    attr = self._addAttribute(row)
    return attr

  def getAttributeByID (self, aid):
    if aid is None:
      return None

    try:
      return self._attributesByID[aid]
    except KeyError:
      pass

    conn = self.connection()
    s = select([tattributes], tattributes.c.id==aid)
    res = conn.execute(s)
    row = res.first()
    if row is None:
      raise UnknownAttributeID(aid)

    attr = self._addAttribute(row)
    return attr

  def getActiveAttributes (self):
    return self._attributesByName.values()

  def resolveUpdateFunc (self, name):
    try:
      return self._updateFuncs[name]
    except KeyError, e:
      pass

    try:
      (mname, fname) = name.rsplit('.', 1)
      mod = importlib.import_module(mname)
      fobj = getattr(mod, fname)
      self._updateFuncs[name] = fobj
      self.log.debug("Resolved update func %s" % (name))
      return fobj
    except AttributeError, e:
      self.log.warning("Couldn't find update function %s in module %s" % (fname, mname))
    except ImportError, e:
      self.log.warning("Couldn't find module %s for update function %s" % (mname, fname))
    except Exception, e:
      self.log.exception("Import Exception", e)

  def _addAttribute (self, row):
    attr = auth.Attribute()
    attr.id = row[tattributes.c.id]
    attr.name = row[tattributes.c.name]
    attr.desc = row[tattributes.c.desc]
    self._attributesByID[attr.id] = attr
    self._attributesByName[attr.name] = attr

    return attr
    
  def createAttribute (self, attr):
    conn = self.connection()
    ins = tattributes.insert().values(name=attr.name, desc=attr.desc)
    res = conn.execute(ins)
    attr.id = res.inserted_primary_key[0]
    self.commit()
    self._attributesByID[attr.id] = attr
    self._attributesByName[attr.name] = attr


### Standard type coercion utilities ###
def coerceBool (key, newval):
  if type(newval) is bool:
    return newval
  if newval.lower().strip() == "true":
    return True
  elif newval.lower().strip() == "false":
    return False
  raise InvalidBooleanInput(newval)


ConfigDB = _DB()

@event.listens_for(engine, "before_execute")
def _log_execute (conn, clauseelement, multiparams, params):
  if isinstance(clauseelement, (expression.Insert, expression.Update, expression.Delete)):
    ConfigDB.log.debug("Lock %s" % (type(clauseelement)))

@event.listens_for(engine, "commit")
def _log_commit (conn):
  ConfigDB.log.debug("Unlock (commit)")

@event.listens_for(engine, "rollback")
def _log_rollback (conn):
  ConfigDB.log.debug("Unlock (rollback)")

