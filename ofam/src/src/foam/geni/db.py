# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

from flask import request_tearing_down, current_app

from sqlalchemy import (Table, Column, MetaData, ForeignKey, Integer, String, Boolean,
                        Text, PickleType, DateTime, Enum, Float, create_engine, func,
                        select, event, and_, or_, not_)
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import expression

from lxml import etree as ET
import uuid
import datetime
import hashlib
import logging
import logging.handlers
import os.path

from foam.config import DB_ENGINE, LOGDIR, HTPASSWDFILE, DB_PATH
from foam.core.log import KeyAdapter
from foam.core.configdb import ConfigDB, ConfigItem, UnknownConfigKey
from foam.core.exception import CoreException
from foam.core.htpasswd import HtpasswdFile
from foam.lib import _asUTC

engine = create_engine(DB_ENGINE)
metadata = MetaData(bind=engine)

SQLFORMAT = "%(asctime)s %(message)s"
CURRENT_VERSION = 1

lhandle = logging.handlers.RotatingFileHandler('%s/genidb.log' % LOGDIR,
                                               maxBytes = 1000000, backupCount=10)
lhandle.setLevel(logging.DEBUG)
lhandle.setFormatter(logging.Formatter(SQLFORMAT))
logging.getLogger('sqlalchemy.engine').addHandler(lhandle)
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

foamlog = logging.getLogger('foam')

slivers = Table('slivers', metadata,
    Column('id', Integer, primary_key=True),
    Column('slice_urn', String(256)),
    Column('sliver_urn', String(256)),
    Column('fvslicename', String(500)),
    Column('req_rspec', Text),
    Column('manifest_rspec', Text),
    Column('parsed_obj', PickleType),
    Column('expiration', PickleType),
    Column('creation', PickleType),
    Column('priority', Integer),
    Column('status', Boolean, default=None),
    Column('deleted', Boolean, default=False))

datapaths = Table('datapaths', metadata,
    Column('id', Integer, primary_key=True),
    Column('dpid', String(23)),
    Column('urn', String(256)),
    Column('location_country', String(3)),
    Column('location_lat', Float),
    Column('location_long', Float),
    Column('persistent', Boolean, default=True),
    Column('persistent_ports', Boolean, default=False),
    Column('description', Text))

class UnknownSlice(CoreException):
  def __init__ (self, urn):
    super(UnknownSlice, self).__init__()
    self.urn = urn
  def __str__ (self):
    return "Slice %s is not known at this aggregate" % (self.urn)

class UnknownSliver(CoreException):
  def __init__ (self, urn):
    super(UnknownSliver, self).__init__()
    self.urn = urn
  def __str__ (self):
    return "Referenced sliver (%s) is not known to this aggregate." % (self.urn)

class UnknownNode(CoreException):
  def __init__ (self, urn):
    super(UnknownNode, self).__init__()
    self.cid = urn
  def __str__ (self):
    return "Referenced node (%s) is not known to this aggregate." % (self.cid)

class _DB(object):
  def __init__ (self):
    self.session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                               bind=engine, expire_on_commit=False))
    self.log = KeyAdapter("GeniDB", logging.getLogger("foam"))
    if not os.path.exists(DB_PATH):
      self.__initDB()
    
#  @property
#  def session (self):
#    if self._session == None:
##      self.log.debug("Creating session")
#      self._session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
#                                                  bind=engine, expire_on_commit=False))
#    if not self._session.is_active:
#      self.log.warn("Rolling back inactive session")
#      self._session.rollback()
#    return self._session
#
#  @session.deleter
#  def session (self):
##    self.log.debug("Deleting session")
#    self._session.remove()
#
#  def close (self, sender, **extra):
##    self.log.debug("Session close")
#    if self._session is not None:
#      self._session.remove()
#      self._session = None

  def connection (self):
#    self.log.debug("Getting connection")
    return self.session.connection()

  def commit (self):
#    self.log.debug("Commit")
    self.session.commit()

  def __initDB (self):
    htp = HtpasswdFile(HTPASSWDFILE, create=True)
    htp.update("foamadmin", "admin")
    htp.save()

    metadata.drop_all()
    metadata.create_all()

    try:
      veritem = ConfigDB.getConfigItemByKey("geni.db-version")
      veritem.setValue(CURRENT_VERSION)
    except UnknownConfigKey, e:
      veritem = ConfigItem().setKey('geni.db-version').setValue(CURRENT_VERSION) \
                  .setDesc("GENI Database schema version")  \
                  .setUpdateFuncName("foam.geni.db.updateVersion") 
      ConfigDB.createConfigItem(veritem)

  def getManifest (self, sliver_urn):
    s = select([slivers], and_(slivers.c.sliver_urn==sliver_urn, slivers.c.deleted==False))
    conn = self.connection()
    result = conn.execute(s)
    row = result.first()
    return row[slivers.c.manifest_rspec]

  def getRspec (self, sliver_urn):
    s = select([slivers], slivers.c.sliver_urn==sliver_urn)
    conn = self.connection()
    result = conn.execute(s)
    row = result.first()
    return row[slivers.c.req_rspec]

  def refreshDevices (self, devices = None):
    from foam.flowvisor import Connection as FV

    if devices is None:
      devices = FV.getDeviceList()

    for dpid in devices:
      dpid = dpid.lower()
      s = select([datapaths], datapaths.c.dpid==dpid)
      conn = self.connection()
      result = conn.execute(s)
      row = result.first()
      if not row:
        switch_urn = generateSwitchComponentID(dpid)
        ins = datapaths.insert().values(dpid=dpid,urn=switch_urn.lower())
        conn.execute(ins)
        self.commit()

  def getLocationData (self, dpid, switch_urn=None):
    # Right now this just inserts DPIDs we haven't seen before
    dpid = dpid.lower()
    s = select([datapaths], datapaths.c.dpid==dpid)
    conn = self.connection()
    result = conn.execute(s)
    row = result.first()
    if not row:
      ins = datapaths.insert().values(dpid=dpid,urn=switch_urn.lower())
      conn.execute(ins)
      self.commit()
    return None

  def getSwitchDPID (self, urn):
    s = select([datapaths], datapaths.c.urn==urn.lower())
    conn = self.connection()
    result = conn.execute(s)
    row = result.first()
    if (not row) and (ConfigDB.importing):
      try:
        dpid = urn.lower().split("datapath+")[1]
      except IndexError, e:
        dpid = urn.lower().split("datapath:")[1]
      ins = datapaths.insert().values(dpid=dpid, urn=urn.lower())
      conn.execute(ins)
      self.commit()
      return dpid
    elif not row:
      raise UnknownNode(urn)
    return row[datapaths.c.dpid]

  def getSliverData (self, sliver_urn, detail=False):
    s = select([slivers], slivers.c.sliver_urn==sliver_urn)
    conn = self.connection()
    result = conn.execute(s)
    row = result.first()
    if not row:
      raise UnknownSliver(sliver_urn)
    return self.makeSliverDataDict(row, detail)

  def getSliverURN (self, slice_urn, deleted = False):
    s = select([slivers], and_(slivers.c.slice_urn==slice_urn, slivers.c.deleted==deleted))
    conn = self.connection()
    result = conn.execute(s)
    row = result.first()
    if not row:
      raise UnknownSlice(slice_urn)
    return row[slivers.c.sliver_urn]

  def getSliverPriority (self, sliver_urn):
    s = select([slivers], slivers.c.sliver_urn==sliver_urn)
    conn = self.connection()
    result = conn.execute(s)
    row = result.first()
    if not row:
      raise UnknownSliver(sliver_urn)
    return row[slivers.c.priority]

  def getEnabled (self, sliver_urn, deleted = False):
    from foam.flowvisor import Connection as FV

    s = select([slivers], and_(slivers.c.sliver_urn==sliver_urn, slivers.c.deleted==deleted))
    conn = self.connection()
    result = conn.execute(s)
    row = result.first()
    if not row:
      raise UnknownSliver(sliver_urn)
    return FV.sliceExists(row[slivers.c.fvslicename])

  def deleteSliver (self, slice_urn=None, sliver_urn=None):
    if slice_urn:
      u = slivers.update().where(slivers.c.slice_urn==slice_urn).values(deleted=True)
    elif sliver_urn:
      u = slivers.update().where(slivers.c.sliver_urn==sliver_urn).values(deleted=True)
    conn = self.connection()
    result = conn.execute(u)
    self.commit()

  def getFlowvisorSliceName (self, slice_urn=None, sliver_urn=None, deleted = False):
    if slice_urn:
      s = select([slivers], and_(slivers.c.slice_urn==slice_urn, slivers.c.deleted==deleted))
    elif sliver_urn:
      s = select([slivers], and_(slivers.c.sliver_urn==sliver_urn, slivers.c.deleted==deleted))

    conn = self.connection()
    result = conn.execute(s)
    row = result.first()
    if row:
      return row[slivers.c.fvslicename]
    else:
      if slice_urn:
        raise UnknownSlice(slice_urn)
      elif sliver_urn:
        raise UnknownSliver(sliver_urn)

  def sliceExists (self, slice_urn, deleted = False):
    s = select([slivers], and_(slivers.c.slice_urn==slice_urn, slivers.c.deleted==deleted))
    conn = self.connection()
    result = conn.execute(s)
    if result.first() is None:
      return False
    return True

  def convertManifestRspec (self, rspec):
    # Temporary magic until we have a real manifest with flowentries in it
    mrspec = rspec.replace('type="request"', 'type="manifest"', 1)
    mrspec = mrspec.replace('request.xsd', 'manifest.xsd', 1)
    return mrspec

  def insertSliver (self, slice_urn, obj, rspec, exp):
    urn = obj.generateURN(slice_urn)
    obj.setSliverURN(urn)
    mrspec = self.convertManifestRspec(rspec)
    ins = slivers.insert().values(slice_urn = slice_urn, sliver_urn = urn, fvslicename = str(obj.getUUID()),
              req_rspec = rspec, manifest_rspec = mrspec, parsed_obj = obj, expiration = exp,
              creation = _asUTC(datetime.datetime.utcnow()))
    conn = self.connection()
    conn.execute(ins)
    self.commit()

  def updateSliverObj (self, sliver_urn, obj):
    u = slivers.update().where(slivers.c.sliver_urn==sliver_urn).values(parsed_obj=obj)
    conn = self.connection()
    result = conn.execute(u)
    self.commit()

  def updateSliverExpiration (self, sliver_urn, exp):
    u = slivers.update().where(slivers.c.sliver_urn==sliver_urn).values(expiration=exp)
    conn = self.connection()
    result = conn.execute(u)
    self.commit()

  def getSliverExpiration (self, sliver_urn):
    s = select([slivers.c.expiration], and_(slivers.c.sliver_urn == sliver_urn, slivers.c.deleted==False))
    conn = self.connection()
    result = conn.execute(s)
    row = result.first()
    return row[slivers.c.expiration]


  def getSliverList (self, deleted = False, status = 0, objs = False):
    if status == 0:
      s = select([slivers], slivers.c.deleted==deleted)
    else:
      s = select([slivers], and_(slivers.c.deleted==deleted, slivers.c.status==status))

    conn = self.connection()
    result = conn.execute(s)
    sl = []
    for row in result:
      if objs:
        sl.append(row[slivers.c.parsed_obj])
      else:
        sl.append(self.makeSliverDataDict(row))
    return sl

  def getExpiredSliverList (self, now):
    s = select([slivers], and_(slivers.c.deleted==False, slivers.c.expiration<=now))
    conn = self.connection()
    result = conn.execute(s)
    sl = []
    for row in result:
      sl.append(self.makeSliverDataDict(row))
    return sl

  def xlateSliverStatus (self, status):
    if status is None:
      return "Pending"
    elif status is True:
      return "Approved"
    elif status is False:
      return "Rejected"

  def makeSliverDataDict (self, row, include_obj = True):
    from foam.flowvisor import Connection as FV
    data = {"id" : row[slivers.c.id], "slice_urn" : row[slivers.c.slice_urn],
      "sliver_urn" : row[slivers.c.sliver_urn], "flowvisor_slice" : row[slivers.c.fvslicename],
      "enabled" : FV.sliceExists(row[slivers.c.fvslicename]),
      "expiration" : str(row[slivers.c.expiration]),
      "creation" : str(row[slivers.c.creation]),
      "status" : self.xlateSliverStatus(row[slivers.c.status]),
      "deleted" : str(row[slivers.c.deleted])}

    if include_obj:
      slobj = row[slivers.c.parsed_obj]
      if slobj:  # Imported slivers don't have sliver objs
        objdata = slobj.getDataDict(False)
        data.update(objdata)
    return data

  def getSliverObj (self, sliver_urn):
    s = select([slivers.c.parsed_obj], slivers.c.sliver_urn==sliver_urn)
    conn = self.connection()
    result = conn.execute(s)
    row = result.first()
    if row is None:
      raise UnknownSliver(sliver_urn)
    return row[slivers.c.parsed_obj]

  def setSliverStatus (self, sliver_urn, status):
    # Can be True (approved), False (rejected), Pending (None)
    u = slivers.update().where(slivers.c.sliver_urn==sliver_urn).values(status=status)
    conn = self.connection()
    result = conn.execute(u)
    self.commit()

  def setSliverPriority (self, sliver_urn, priority):
    u = slivers.update().where(slivers.c.sliver_urn==sliver_urn).values(priority=priority)
    conn = self.connection()
    result = conn.execute(u)
    self.commit()

  def insertFinalStats (self, slice_urn, stats):
    return

  def seenDPID (self, dpid):
    s = select([datapaths], datapaths.c.dpid==dpid)
    conn = self.connection()
    result = conn.execute(s)
    if result.first():
      return True
    else:
      return False

  def setLocation (self, dpid, country, lat, lon):
    conn = self.connection()
    if not seenDPID(dpid):
      switch_urn = generateSwitchComponentID(dpid)
      i = datapaths.insert().values(dpid = dpid, urn = switch_urn, location_country = country,
                                    location_lat = lat, location_long = lon)
      res = conn.execute(i)
    else:
      u = datapaths.update().where(datapaths.c.dpid==dpid).values(location_country = country, location_lat = lat,
                                                                  location_long = lon)
      res = conn.execute(u)
    self.commit()
    
  def addDatapath (self, dpid):
    conn = self.connection()
    if not self.seenDPID(dpid):
      switch_urn = generateSwitchComponentID(dpid).lower()
      i = datapaths.insert().values(dpid = dpid, urn = switch_urn)
      res = conn.execute(i)
    self.commit()

  def removeDatapath (self, dpid):
    conn = self.connection()
    d = datapaths.delete().where(datapaths.c.dpid==dpid)
    r = conn.execute(d)
    self.commit()

  def getDeviceSet (self):
    conn = self.connection()
    s = select([datapaths.c.dpid])
    result = conn.execute(s)
    dpids = set()
    for row in result:
      dpids.add(row[datapaths.c.dpid])
    return dpids

  def rebuildDatapathURNs (self, tag):
    new_data = []
    conn = self.connection()
    s = select([datapaths])
    res = conn.execute(s)
    for row in res:
      newurn = generateSwitchComponentID(row[datapaths.c.dpid], tag).lower()
      new_data.append((row[datapaths.c.id], newurn))
    for (did, newurn) in new_data:
      u = datapaths.update().where(datapaths.c.id==did).values(urn=newurn)
      res = conn.execute(u)
    self.commit()

def getManagerID ():
  tag = ConfigDB.getConfigItemByKey("geni.site-tag").getValue()
  return "urn:publicid:IDN+openflow:foam:%s+authority+am" % (tag)

def generateSwitchComponentID (dpid, tag = None):
  if tag is None:
    tag = ConfigDB.getConfigItemByKey("geni.site-tag").getValue()
  return "urn:publicid:IDN+openflow:foam:%s+datapath+%s" % (tag, dpid)

GeniDB = _DB()

@event.listens_for(engine, "before_execute")
def _log_execute (conn, clauseelement, multiparams, params):
  if isinstance(clauseelement, (expression.Insert, expression.Update, expression.Delete)):
    GeniDB.log.debug("Lock %s" % (type(clauseelement)))

@event.listens_for(engine, "commit")
def _log_commit (conn):
  GeniDB.log.debug("Unlock (commit)")

@event.listens_for(engine, "rollback")
def _log_rollback (conn):
  GeniDB.log.debug("Unlock (rollback)")

