# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University
# Copyright (c) 2012  Barnstormer Softworks, Ltd.

import xmlrpclib
import jsonrpc
import logging
import datetime
import time

from foam.core.log import KeyAdapter
from foam.openflow.types import Port
import foam.core.allocation

MAXAGE = datetime.timedelta(hours=6)

class CachedSlice(object):
  def __init__ (self, name):
    self.name = name 
    self._time = datetime.datetime.now()
    self._info = Connection.getSliceInfo(self.name)

  def exists (self):
    now = datetime.datetime.now()
    if (now - self._time) > MAXAGE:
      self._time = now
      self._info = Connection.getSliceInfo(self.name)
    if self._info is not None:
      return True
    else:
      return False


class SliceCache(object):
  def __init__ (self):
    self._cache = {}

  def exists (self, slice_name):
    try:
      return self._cache[slice_name].exists()
    except KeyError, e:
      sl = CachedSlice(slice_name)
      self._cache[slice_name] = sl
      return sl.exists()

  def delete (self, slice_name):
    try:
      del self._cache[slice_name]
    except:
      return

  def add (self, slice_name):
    self._cache[slice_name] = CachedSlice(slice_name)


class _Connection(object):
  def __init__ (self):
    self.xmlcall = self._xmlcall_time

    self.log = KeyAdapter("svc:FV", logging.getLogger('foam'))
    self.plog = logging.getLogger("perf")
    self.__host = ConfigDB.getConfigItemByKey("flowvisor.hostname").getValue()
    self.__passwd = ConfigDB.getConfigItemByKey("flowvisor.passwd").getValue()
    self.__jsonport = ConfigDB.getConfigItemByKey("flowvisor.json-port").getValue()
    self.__xmlport = ConfigDB.getConfigItemByKey("flowvisor.xmlrpc-port").getValue()
    self.__sliceCache = SliceCache()
    self.buildConnections()

  def updateConfig (self, info):
    self.info = info
    self.buildConnections()
    self.rebuildCache()

  def buildConnections (self):
    self.xmlconn = xmlrpclib.ServerProxy("https://fvadmin:%s@%s:%d/xmlrpc" % (
      self.__passwd, self.__host, self.__xmlport))   
    self.jsonconn = jsonrpc.ServiceProxy("https://fvadmin:%s@%s:%d" % (
      self.__passwd, self.__host, self.__jsonport))

  def _xmlcall_time (self, method, *args):
    m = getattr(self.xmlconn, "api.%s" % (method))
    t1 = time.time()
    ret = m(*args)
    dur = time.time() - t1
    self.plog.info("FlowVisor:%s %.2f" % (method, dur * 1000))
    return ret

  def _xmlcall_fast (self, method, *args):
    m = getattr(self.xmlconn, "api.%s" % (method))
    return m(*args)
  
  def rebuildCache (self):
    self.__sliceCache = SliceCache()

  def getDeviceList (self):
    self.log.debug("XMLRPC:ListDevices")
    dl = self.xmlcall("listDevices")
    dl.sort()
    return dl

  def getLinkList (self):
    self.log.debug("XMLRPC:getLinks")
    return self.xmlcall("getLinks")
    
  def getFVVersion (self):
    self.log.debug("XMLRPC:getFVVersion")
    self.fvversion = self.xmlcall("ping", "")
    return self.fvversion

  def getDevicePorts (self, dpid):
    self.log.debug("XMLRPC:getDeviceInfo (%s)" % (dpid))
    
    pinfoall = []
    if "vertigo" in self.fvversion:
      pinfoall = self.xmlcall("getVTPlannerPortInfo", dpid, "all")
      
    portlist = []
    dinfo = self.xmlcall("getDeviceInfo", dpid)
    for portstr in dinfo["portNames"].split(","):
      p = Port()
      elems = portstr.split("(")
      p.name = elems[0]
      p.num = int(elems[1][:-1])
      
      for pinfo in pinfoall:
        pelems = pinfo.split(",")
        if int(pelems[0]) == p.num:
          p.features = pelems[2]
          break
      
      p.dpid = dpid
      portlist.append(p)
    return portlist

  def getCombinedStats (self, slice_name):
    return None

  def deleteSlice (self, slice_name):
    self.log.debug("XMLRPC:deleteSlice (%s)" % (slice_name))
    self.xmlcall("deleteSlice", slice_name)
    self.__sliceCache.delete(slice_name)

  def sliceExists (self, slice_name):
    return self.__sliceCache.exists(slice_name)

  def getSliceInfo (self, slice_name):
    self.log.debug("XMLRPC:getSliceInfo (%s)" % (slice_name))
    try:
      sinfo = self.xmlcall("getSliceInfo", slice_name)
      return sinfo
    except:
      return None

  def createSlice (self, slice_name, controller, email):
    self.log.debug("XMLRPC:createSlice (%s, %s, %s)" % (slice_name, controller, email))
    self.xmlcall("createSlice", slice_name, self.__passwd, controller, email)
    self.__sliceCache.add(slice_name)

  def changeFlowspace (self, opslist):
    self.log.debug("XMLRPC:changeFlowSpace")
    self.xmlcall("changeFlowSpace", opslist)
  
  def addVirtualLink (self, slice_name,action):
    self.log.debug("XMLRPC:addVirtualLink")
    self.xmlcall("addLink", slice_name,action)

  def updateInfo (self, key, value):
    if key == "flowvisor.hostname":
      self.__host = value
    elif key == "flowvisor.passwd":
      self.__passwd = value
    elif key == "flowvisor.json-port":
      self.__jsonport = value
    elif key == "flowvisor.xmlrpc-port":
      self.__xmlport = value
    elif key == "flowvisor.record-rpc-timing":
      v = coerceBool(key, value)
      if v:
        self.xmlcall = self._xmlcall_time
      else:
        self.xmlcall = self._xmlcall_fast
    self.buildConnections()
    return value

def updateInfo (key, value):
  return Connection.updateInfo(key, value)

class FSAllocation(foam.core.allocation.Allocation):
  def __init__ (self):
    super(FSAllocation, self).__init__()

    self._groups = {}
    self._flowspecs = []
    self._virtuallinks = []
    self._controllers = []

  def __str__ (self):
    x = super(FSAllocation, self).__str__()
    return "<FV:Allocation:\n Controllers:\n%s\n Groups:\n%s\n Flowspace:\n%s\n VirtualLinks:\n%s>\n" % (
      "\n  ".join([str(x) for x in self._controllers]),
      "\n  ".join(["%s: %s" % (k, "\n   ".join(str(x) for x in v)) for k,v in self._groups.iteritems()]),
      "\n  ".join([str(x) for x in self._flowspecs]), 
      "\n  ".join([str(x) for x in self._virtuallinks]))

  def getDataDict (self, detail = True):
    obj = super(FSAllocation, self).getDataDict(detail)
    if detail:
      dobj = {"controllers" : [x.__json__() for x in self._controllers],
              "flowspace rules" : len(self.generateFlowEntries())}
      obj.update(dobj)
    return obj

  def getGroups (self):
    return self._groups

  def getFlowspecs (self):
    return self._flowspecs
  
  def getVirtualLinks (self):
    return self._virtuallinks

  def getControllers (self):
    return self._controllers

  def addGroup (self, name, dplist = []):
    if name is None:
      raise NoGroupName()
    if self._groups.has_key(name):
      raise GroupNameAlreadyUsed(name)
    self._groups[name] = dplist

  def addDatapathToGroup (self, gname, dp):
    self._groups.setdefault(gname, []).append(dp)

  def addController (self, controller):
    self._controllers.append(controller)

  def addFlowSpec (self, fs):
    self._flowspecs.append(fs)
   
  def addVirtualLink (self, vl):
    self._virtuallinks.append(vl)

  def getGroupDatapaths (self, gname):
    return self._groups[gname]

  def validate (self):
    cs = [x for x in self._controllers if x.type == "primary"]
    if len(cs) == 0:
      raise NoPrimaryController()
    elif len(cs) > 1:
      raise TooManyPrimaryControllers()

  def createSlice (self):
    cs = [x for x in self._controllers if x.type == "primary"]
    if len(cs) == 0:
      raise NoPrimaryController()
    Connection.createSlice(str(self.getUUID()), cs[0].url, self.getEmail())

  def generateFlowEntries (self, priority=100):
    entries = []
    for fs in self._flowspecs:
      entries.extend(fs.generateFlowEntries(priority, self._groups.get(None, [])))
    return entries

  def insertFlowspace (self, priority):
    flowspace = self.generateFlowEntries(priority)
    action = "Slice:%s=4" % (self.getUUID())

    ops = []
    for entry in flowspace:
      match = entry[2]
      if match == "any":
        match = "OFMatch[]"
      ops.append({"operation" : "ADD", "dpid" : entry[0], "priority" : str(entry[1]),
        "match" : match, "actions" : action})
    Connection.changeFlowspace(ops)
  
  def generateVLinkEntries (self):
    entries = []
    for fs in self._virtuallinks:
      entries.extend(fs.generateVLinkEntries())
    return entries
    
  def insertVirtualLink (self):
    vlinks = self.generateVLinkEntries()
    slicename = "%s" % (self.getUUID())
    for action in vlinks:
      Connection.addVirtualLink(slicename,action)

from foam.core.configdb import ConfigDB, ConfigItem, coerceBool

citems = []
citems.append(ConfigItem().setKey("flowvisor.hostname").setValue(None)
              .setDesc("Flowvisor hostname or IP address")
              .setUpdateFuncName("foam.flowvisor.updateInfo"))
citems.append(ConfigItem().setKey("flowvisor.json-port").setValue(8081)
              .setDesc("Flowvisor JSON RPC port")
              .setUpdateFuncName("foam.flowvisor.updateInfo"))
citems.append(ConfigItem().setKey("flowvisor.xmlrpc-port").setValue(8080)
              .setDesc("Flowvisor XMLRPC port")
              .setUpdateFuncName("foam.flowvisor.updateInfo"))
citems.append(ConfigItem().setKey("flowvisor.passwd").setValue(None)
              .setDesc("Flowvisor fvadmin password")
              .setUpdateFuncName("foam.flowvisor.updateInfo"))
citems.append(ConfigItem().setKey("flowvisor.record-rpc-timing").setValue(True)
              .setDesc("Record timing info for FlowVisor RPC calls")
              .setUpdateFuncName("foam.flowvisor.updateInfo"))

[ConfigDB.installConfigItem(x) for x in citems]
del citems

Connection = _Connection()

