# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

from lxml import etree as ET
from lxml import etree
import datetime
import itertools
import traceback
import pprint
import copy
import dateutil
import logging

from foam.core.exception import CoreException
from foam.core.configdb import ConfigDB

class NoGroupName(CoreException):
  def __init__ (self):
    super(NoGroupName, self).__init__()
  def __str__ (self):
    return "A group was configured with no name specified"

class GroupNameAlreadyUsed(CoreException):
  def __init__ (self, name):
    super(GroupNameAlreadyUsed, self).__init__()
    self.name = name
  def __str__ (self):
    return "The group name (%s) is defined more than once in the request." % (self.name)


class BadSliverExpiration(CoreException):
  def __init__ (self, msg):
    super(BadSliverExpiration, self).__init__()
    self.msg = msg
  def __str__ (self):
    return self.msg

def renewSliver (slice_urn, creds, exptime):
  from foam.geni.db import GeniDB

  sliver_urn = GeniDB.getSliverURN(slice_urn)

  reqexp = dateutil.parser.parse(str(exptime))
  reqexp = _asUTC(reqexp)

  max_expiration = _asUTC(datetime.datetime.utcnow()) + ConfigDB.getConfigItemByKey("geni.max-lease").getValue()

  if reqexp > max_expiration:
    raise BadSliverExpiration(
      "The requested expiration date (%s) is past the allowed maximum expiration (%s)." %
        (reqexp, max_expiration))

  for cred in creds:
    credexp = _asUTC(cred.expiration)
    if reqexp > credexp:
      continue
    else:
      GeniDB.updateSliverExpiration(sliver_urn, reqexp)
      sobj = GeniDB.getSliverObj(sliver_urn)
      sobj.resetExpireEmail()
      sobj.store()
      return sliver_urn

  raise BadSliverExpiration(
      "No credential found whose expiration is greater than or equal to the requested sliver expiration (%s)" %
        (reqexp))

def _asUTC(dt):
    tz_utc = dateutil.tz.tzutc()
    if dt.tzinfo:
      dt = dt.astimezone(tz_utc)
    else:
      dt = dt.replace(tzinfo=tz_utc)
    return dt

class VirtualLink(object):
  def __init__ (self):
    self.bound_datapaths = {}
    self.__vlinks = []
    
  def __str__ (self):
    return "virtual_link: %s" % (",".join([str(x) for x in self.__vlinks]))
    
  def bindDatapath (self, dp):
    if dp.dpid in self.bound_datapaths:
      self.bound_datapaths[dp.dpid].merge(dp)
    else:
      self.bound_datapaths[dp.dpid] = copy.deepcopy(dp)
      
  def generateVLinkEntries (self):
    vlrules = []
    for entry in self.__vlinks:
      if entry: vlrules.append(entry)
    return vlrules
      
  def addVLinkFromString (self, vstr):
    self.__vlinks.append(vstr.strip())

class FlowSpec(object):
  def __init__ (self):
    self.bound_datapaths = {}
    self.__dlsrc = []
    self.__dldst = []
    self.__dltype = []
    self.__vlanid = []
    self.__nwsrc = []
    self.__nwdst = []
    self.__nwproto = []
    self.__tpsrc = []
    self.__tpdst = []

  def bindDatapath (self, dp):
    if dp.dpid in self.bound_datapaths:
      self.bound_datapaths[dp.dpid].merge(dp)
    else:
      self.bound_datapaths[dp.dpid] = copy.deepcopy(dp)
      
  def __str__ (self):
    return "dl_src=%s; dl_dst=%s; dl_type:%s; vlan_id: %s;\n" \
        "    nw_src: %s; nw_dst: %s; nw_proto: %s; tp_src: %s; tp_dst: %s" % (
            ",".join([str(x) for x in self.__dlsrc]),
            ",".join([str(x) for x in self.__dldst]),
            ",".join([str(x) for x in self.__dltype]),
            ",".join([str(x) for x in self.__vlanid]),
            ",".join([str(x) for x in self.__nwsrc]),
            ",".join([str(x) for x in self.__nwdst]),
            ",".join([str(x) for x in self.__nwproto]),
            ",".join([str(x) for x in self.__tpsrc]),
            ",".join([str(x) for x in self.__tpdst]))

  def __json__ (self):
    return {"datapaths" : self.bound_datapaths,
            "dl_src" : self.__dlsrc,
            "dl_dst" : self.__dldst,
            "dl_type" : self.__dltype,
            "dl_vlan" : self.__vlanid,
            "nw_src" : self.__nwsrc,
            "nw_dst" : self.__nwdst,
            "nw_proto" : self.__nwproto,
            "tp_src" : self.__tpsrc,
            "tp_dst" : self.__tpdst}

  def getMACs (self):
    for x in self.__dlsrc:
      yield x
    for y in self.__dldst:
      yield y

  def getEtherTypes (self):
    for x in self.__dltype:
      yield x

  def getIPSubnets (self):
    for x in self.__nwsrc:
      yield x
    for x in self.__nwdst:
      yield x
			
  #start of Vasileios's code (get the rest of the flowspec data)
  def getVLANs (self):
    for x in self.__vlanid: 
      yield x

  def getNWProtos (self):
    for x in self.__nwproto:
      yield x
		
  def getTPPorts (self):
    for x in self.__tpsrc:
      yield x
    for x in self.__tpdst:
      yield x
	
	#end of Vasileios's code

  def getDatapaths (self):
    return self.bound_datapaths.values()

  def hasVLANs (self):
    if self.__vlanid:
      return True

  def generateFlowEntries (self, priority, datapaths):
    dpports = []
    if len(self.bound_datapaths) > 0:
      datapaths = self.bound_datapaths.values()

    for dpobj in datapaths:
      if dpobj.ports:
        dpports.extend(itertools.product([dpobj.dpid], [p.num for p in dpobj.ports]))
      else:
        dpports.extend(itertools.product([dpobj.dpid], [None]))

    # Handle the "any" case
    if not dpports: dpports.append((None, None))

    # product won't return any values if any dict is empty, so if the values weren't set, add blanks
    if not self.__dlsrc: self.__dlsrc.append(None)
    if not self.__dldst: self.__dldst.append(None)
    if not self.__dltype: self.__dltype.append(None)
    if not self.__vlanid: self.__vlanid.append(None)
    if not self.__nwsrc: self.__nwsrc.append(None)
    if not self.__nwdst: self.__nwdst.append(None)
    if not self.__nwproto: self.__nwproto.append(None)
    if not self.__tpsrc: self.__tpsrc.append(None)
    if not self.__tpdst: self.__tpdst.append(None)

    entries = itertools.product(dpports, self.__dlsrc, self.__dldst, self.__dltype, self.__vlanid,
                                self.__nwsrc, self.__nwdst, self.__nwproto, self.__tpsrc, self.__tpdst)

    fsrules = []
    for entry in entries:
      m = []
      if entry[1]: m.append("dl_src=%s" % entry[1])
      if entry[2]: m.append("dl_dst=%s" % entry[2])
      if entry[3]: m.append("dl_type=%s" % entry[3])
      if entry[4]: m.append("dl_vlan=%s" % entry[4])
      if entry[5]: m.append("nw_src=%s" % entry[5])
      if entry[6]: m.append("nw_dst=%s" % entry[6])
      if entry[7]: m.append("nw_proto=%s" % entry[7])
      if entry[8]: m.append("tp_src=%s" % entry[8])
      if entry[9]: m.append("tp_dst=%s" % entry[9])
      if entry[0][1]: m.append("in_port=%d" % entry[0][1])

      e = []
      if entry[0][0]:
        e.append("%s" % str(entry[0][0]))
      else:
        e.append("any")
      e.append(priority)
      if m:
        e.append("%s" % ",".join(m))
      else:
        e.append("any")
        
      fsrules.append(e)
      
    return fsrules

  def addDlSrcFromString (self, vstr):
    maclist = vstr.split(",")
    for mac in maclist:
      self.__dlsrc.append(mac.strip())

  def addDlDstFromString (self, vstr):
    maclist = vstr.split(",")
    for mac in maclist:
      self.__dldst.append(mac.strip())

  def addDlTypeFromString (self, vstr):
    for dltype in vstr.split(","):
      self.__dltype.append(dltype.strip())
  
  def addVlanIDFromString (self, vstr):
    for vlid in vstr.split(","):
      if vlid.count("-"):
        l = vlid.split("-")
        self.__vlanid.extend(range(int(l[0]), int(l[1])+1))
      else:
        self.__vlanid.append(int(vlid))

  def addNwSrcFromString (self, vstr):
    for nw in vstr.split(","):
      self.__nwsrc.append(nw.strip())
 
  def addNwDstFromString (self, vstr):
    for nw in vstr.split(","):
      self.__nwdst.append(nw.strip())

  def addNwProtoFromString (self, vstr):
    for proto in vstr.split(","):
      if proto.count("-"):
        l = proto.split("-")
        self.__nwproto.extend(range(int(l[0]), int(l[1])+1))
      else:
        self.__nwproto.append(int(proto))

  def addTpSrcFromString (self, vstr):
    for port in vstr.split(","):
      if port.count("-"):
        l = port.split("-")
        self.__tpsrc.extend(range(int(l[0]), int(l[1])+1))
      else:
        self.__tpsrc.append(int(port))
  
  def addTpDstFromString (self, vstr):
    for port in vstr.split(","):
      if port.count("-"):
        l = port.split("-")
        self.__tpdst.extend(range(int(l[0]), int(l[1])+1))
      else:
        self.__tpdst.append(int(port))


class TooManyPrimaryControllers(CoreException):
  def __init__ (self):
    super(TooManyPrimaryControllers, self).__init__()
  def __str__ (self):
    return "More than one primary controller specified."

class NoPrimaryController(CoreException):
  def __init__ (self):
    super(NoPrimaryController, self).__init__()
  def __str__ (self):
    return "A primary controller must be specified."

class NoSliverTag(CoreException):
  def __init__ (self):
    super(NoSliverTag, self).__init__()
  def __str__ (self):
    return "Request contains no sliver."

class NoPacketTag(CoreException):
  def __init__ (self, match):
    super(NoPacketTag, self).__init__()
  def __str__ (self):
    return "Match does not contain a packet specification."

class NoControllersDefined(CoreException):
  def __init__ (self):
    super(NoControllersDefined, self).__init__()
  def __str__ (self):
    return "No controllers are defined for this request."
    
class NoHopsTag(CoreException):
  def __init__ (self):
    super(NoHopsTag, self).__init__()
  def __str__ (self):
    return "VirtualLink does not contain the list of hops."    
