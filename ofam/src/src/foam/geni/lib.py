# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

import traceback
from cStringIO import StringIO
from lxml import etree as ET
from lxml import etree
import datetime
import logging.handlers
import logging

from foam.config import LOGDIR, LOGLEVEL, LOGFORMAT

lhandle = logging.handlers.RotatingFileHandler('%s/gapi-actions.log' % (LOGDIR), maxBytes=1000000)
lhandle.setLevel(LOGLEVEL)
lhandle.setFormatter(logging.Formatter(LOGFORMAT))
actionlog = logging.getLogger('gapi-actions')
actionlog.addHandler(lhandle)
actionlog.setLevel(LOGLEVEL)

import foam.task
import foam.openflow.types
from foam.flowvisor import Connection as FV
from foam.core.json import jsonify, jsonValidate, JSONValidationError
from foam.core.exception import CoreException
from foam.creds import CredVerifier
from foam.lib import NoGroupName, VirtualLink, FlowSpec, _asUTC
from foam.core.configdb import ConfigDB
from foam.geni.db import GeniDB, getManagerID, generateSwitchComponentID, UnknownSliver
from foam.geni.topology import TopoDB
import foam.geni.approval

OFNSv3 = "/opt/ofelia/ofam/local/schemas"
OFNSv4 = "/opt/ofelia/ofam/local/schemas"
PGNS = "/opt/ofelia/ofam/local/schemas"
XSNS = "http://www.w3.org/2001/XMLSchema-instance"

def deleteSliver (slice_urn = None, sliver_urn = None):
  slice_name = GeniDB.getFlowvisorSliceName(slice_urn=slice_urn, sliver_urn = sliver_urn)
  if FV.sliceExists(slice_name):
#    stats = FV.getCombinedStats(slice_name)
#    GeniDB.insertFinalStats(slice_urn, stats)
    FV.deleteSlice(slice_name)
  GeniDB.deleteSliver(slice_urn=slice_urn, sliver_urn=sliver_urn)
  foam.geni.approval.rebuildDB()

def siteTagChange (key, value):
  flog = logging.getLogger('foam')
  flog.warning("Changing site tag to '%s' - regenerating all datapath URNs" % (value))
  GeniDB.rebuildDatapathURNs(value)
  return value

def updateMaxLease (key, value):
  if type(value) is not int:
    value = int(value)
  flog = logging.getLogger('foam')
  tval = datetime.timedelta(hours=value)
  flog.info("Changing geni.max-lease to %s" % (str(tval)))
  return tval

def addAdDevice (rspec, dpid, active=True):
  switch_urn = generateSwitchComponentID(dpid)

  od = ET.SubElement(rspec, "{%s}datapath" % (OFNSv3))
  od.attrib["component_id"] = switch_urn
  od.attrib["component_manager_id"] = getManagerID()
  od.attrib["dpid"] = dpid

  locdata = GeniDB.getLocationData(dpid, switch_urn)
  if locdata:
    ET.SubElement(od, "{%s}location" % (OFNSv3), country=locdata.country, latitude=locdata.lat, longitude=locdata.long)

  attachments = TopoDB.getDPIDAttachments(dpid)

  if active:
    ports = FV.getDevicePorts(dpid)
    for port in ports:
      if (port.features == None):
        p = ET.SubElement(od, "{%s}port" % (OFNSv3), num=str(port.num), name=port.name)
      else:
        p = ET.SubElement(od, "{%s}port" % (OFNSv3), num=str(port.num), name=port.name, features=port.features)
      for info in attachments.setdefault(port.name, []):
        a = ET.SubElement(p, "{%s}attachment" % (OFNSv3))
        a.attrib["remote_component_id"] = info.remote_component_id
        a.attrib["remote_port"] = info.remote_port
        a.attrib["desc"] = info.desc
#getLinks START 
def addAdLink (rspec, link):
  od = ET.SubElement(rspec, "{%s}link" % (OFNSv3))     
  od.attrib["srcDPID"] = link["srcDPID"]
  od.attrib["srcPort"] = link["srcPort"]
  od.attrib["dstDPID"] = link["dstDPID"]
  od.attrib["dstPort"] = link["dstPort"]
#getLinks END 
  
def getAdvertisement ():
  NSMAP = {None: "%s" % (PGNS),
          "xs" : "%s" % (XSNS),
          "openflow" : "%s" % (OFNSv3)}

  rspec = ET.Element("rspec", nsmap = NSMAP)
  rspec.attrib["{%s}schemaLocation" % (XSNS)] = PGNS + " " \
              "http://www.geni.net/resources/rspec/3/ad.xsd " + \
              OFNSv3 + " " \
              "http://www.geni.net/resources/rspec/ext/openflow/3/of-ad.xsd"
  rspec.attrib["type"] = "advertisement"

  links = FV.getLinkList()
  devices = FV.getDeviceList()
  fvversion = FV.getFVVersion()
  db_devices = GeniDB.getDeviceSet()
  GeniDB.refreshDevices(devices)

  for dpid in devices:
    db_devices.discard(dpid)
    addAdDevice(rspec, dpid)

  for dpid in db_devices:
    addAdDevice(rspec, dpid, False)
 
#getLinks START    
  for link in links:
    addAdLink(rspec, link)
#getLinks END 
    
  xml = StringIO()
  ET.ElementTree(rspec).write(xml)
  return xml.getvalue()

def approveSliver (request, logger):
  try:
    jsonValidate(request.json, [("sliver_urn", (unicode,str)), ("priority", int)], logger)

    if (not request.json.has_key("sliver_urn")) or (not request.json.has_key("priority")):
      return jsonify({"exception" : "You must specify a sliver_urn and priority"})
    slice_name = GeniDB.getFlowvisorSliceName(sliver_urn=request.json["sliver_urn"])
    if FV.sliceExists(slice_name):
      return jsonify({"Fault" : "Flowvisor slice '%s' already exists" % (slice_name)})

    sobj = GeniDB.getSliverObj(request.json["sliver_urn"])
    GeniDB.setSliverStatus(request.json["sliver_urn"], True)
    GeniDB.setSliverPriority(request.json["sliver_urn"], request.json["priority"])

    GeniDB.commit()

    foam.geni.approval.AppData.addSliver(sobj)

    sobj.createSlice()
    sobj.insertFlowspace(request.json["priority"])
    sobj.insertVirtualLink()

    data = GeniDB.getSliverData(sobj.getURN(), True)
    foam.task.emailApproveSliver(data)

    return jsonify(None)
  except JSONValidationError, e:
    jd = e.__json__()
    return jsonify(jd, code = 1, msg = jd["exception"])
  except Exception, e:
    logger.exception("Exception")
    return jsonify(None, code = 2, msg  = traceback.format_exc())

def createSliver (slice_urn, credentials, rspec, user_info):
  flog = logging.getLogger('foam')

  if GeniDB.sliceExists(slice_urn):
    raise DuplicateSliver(slice_urn)

  creds = CredVerifier.fromStrings(credentials, "createsliver", slice_urn)
  try:
    s = StringIO(rspec)
    rspec_dom = ET.parse(s)
  except Exception, exc:
    flog.exception("XML rspec parsing error")
    raise RspecParseError(slice_urn, str(exc))

  of3 = open("/opt/ofelia/ofam/local/schemas/of-resv-3.xsd", "r")
  xsdoc3 = etree.parse(of3)
  xs3 = etree.XMLSchema(xsdoc3)

  try:
    xs3.assertValid(rspec_dom)
  except etree.DocumentInvalid, e:
    flog.exception("XML rspec validation error")
    raise RspecValidationError()

  rspec_elem = rspec_dom.getroot()
  schemas = rspec_elem.get("{%s}schemaLocation" % (XSNS))

  expiration = _asUTC(datetime.datetime.utcnow()) + ConfigDB.getConfigItemByKey("geni.max-lease").getValue()
  for cred in creds:
    credexp = _asUTC(cred.expiration)
    if credexp < expiration:
      expiration = credexp

  GeniDB.refreshDevices()

  sliver = GENISliver(rspec_dom)

  sliver.setUserURN(user_info["urn"])
  sliver.setUserEmail(user_info["email"], overwrite=False)
  sliver.validate()

  GeniDB.insertSliver(slice_urn, sliver, rspec, expiration)
  return sliver

class IllegalEthertype(CoreException):
  def __init__ (self, dltype):
    super(IllegalEthertype, self).__init__()
    self.dltype = dltype
  def __str__ (self):
    return "Experimenters may not request ethertype (%s)" % (self.dltype)

class NoExperimenterEmail(CoreException):
  def __init__ (self):
    super(NoExperimenterEmail, self).__init__()
  def __str__ (self):
    return "An email address was not specified in the rspec nor found in the user credential."

class RspecValidationError(CoreException):
  def __init__ (self):
    pass
  def __str__ (self):
    return "XML Schema validation error parsing request rspec."

class RspecParseError(CoreException):
  def __init__ (self, slice_urn, error):
    self.slice_urn = slice_urn
    self.err_msg = error
  def __str__ (self):
    return "Can't create sliver for slice %s - Exception parsing rspec: %s" % (self.slice_urn, self.err_msg)

class DuplicateSliver(CoreException):
  def __init__ (self, urn):
    self.slice_urn = urn
  def __str__ (self):
    return "Sliver for slice %s already exists." % (self.slice_urn)

class UnmanagedComponent(CoreException):
  def __init__ (self, cid):
    self.cid = cid
  def __str__ (self):
    return "Component (%s) is not managed by this aggregate." % (self.cid)

class UnknownComponentManagerID(CoreException):
  def __init__ (self, cid):
    self.cid = cid
  def __str__ (self):
    return "Specified component manager (%s) is not this aggregate." % (self.cid)

class ComponentManagerIDMismatch(CoreException):
  def __init__ (self, cid, cmid):
    self.cid = cid
    self.cmid = cmid
  def __str__ (self):
    return "Component ID (%s) is not a member of specified manager (%s)." % (self.cid, self.cmid)

class GENIDatapath(foam.openflow.types.Datapath):
  def __init__ (self, dom):
    super(GENIDatapath, self).__init__()

    self.component_id = None

    if dom.tag == u'{%s}datapath' % (OFNSv3):
      self.__parse_openflowv3_datapath(dom)

  def __parse_openflowv3_datapath (self, dom):
    self.component_id = dom.get("component_id")
    cmid = dom.get("component_manager_id")
    if self.component_id.count(cmid[:-12]) != 1:
      raise ComponentManagerIDMismatch(self.component_id, cmid)
    if cmid != getManagerID():
      raise UnknownComponentManagerID(self.component_id)
    self.dpid = GeniDB.getSwitchDPID(self.component_id)
    self.ports = set()
    for port in dom.findall('{%s}port' % (OFNSv3)):
      p = foam.openflow.types.Port()
      p.num = int(port.get("num"))
      p.dpid = self.dpid
      self.ports.add(p)

  def __str__ (self):
    return "[%s] %s\n%s\n" % (self.dpid, self.component_id,
        "    ".join(["%s" % (str(x)) for x in self.ports]))

  def __json__ (self):
    return {"dpid" : self.dpid, "component" : self.component_id,
            "ports" : [x.__json__() for x in self.ports]}

def getSliverStatus (sliver_urn):
  try:
    slice_name = GeniDB.getFlowvisorSliceName(sliver_urn=sliver_urn)
    if FV.sliceExists(slice_name):
      return "ready"
    else:
      return "configuring"
  except Exception, e:
    return "failed"

def importSliver (opts):
  # Quick dirty way to find out if a sliver exists
  try:
    GeniDB.getSliverPriority(opts["sliver_urn"])
    return
  except UnknownSliver, e:
    pass

  s = StringIO(str(opts["req_rspec"]))
  rspec_dom = ET.parse(s)
  root_elem = rspec_dom.getroot()

  sliver = GENISliver(rspec_dom)
  sliver._uuid = opts["fvslicename"]
  GeniDB.insertSliver(opts["slice_urn"], sliver, str(opts["req_rspec"]), opts["exp"])
  GeniDB.setSliverPriority(opts["sliver_urn"], opts["priority"])
  GeniDB.setSliverStatus(opts["sliver_urn"], opts["status"])
  if opts["deleted"]:
    GeniDB.deleteSliver(sliver_urn = opts["sliver_urn"])

class GENISliver(foam.flowvisor.FSAllocation):
  def __init__ (self, dom):
    super(GENISliver, self).__init__()

    self.__urn = None
    self.__slice_urn = None
    self.__user_urn = None
    self.__ref = None
    self.__pend_reason = None

    if dom:
      self.__parseDatav3(dom)

  def __str__ (self):
    x = super(GENISliver, self).__str__()
    return "<GENI Sliver: %s\n %s, %s>\n%s" % (self.__ref, self.__urn, self.__user_urn, x)

  def __json__ (self):
    data = self.getDataDict(True)
    if self.__urn:
      dbdata = GeniDB.getSliverData(self.__urn, False)
      data.update(dbdata)
    return data

  def store (self):
    GeniDB.updateSliverObj(self.__urn, self)

  def json_flowspec (self):
    return {"groups" : [{k : [x.__json__() for x in v]} for k,v in self._groups.iteritems()],
            "flowspecs" : [x.__json__() for x in self._flowspecs]}

  def setPendReason (self, reason):
    self.__pend_reason = reason

  def getURN (self):
    return self.__urn

  def getSliceURN (self):
    return self.__slice_urn

  def getUserURN (self):
    return self.__user_urn

  def makeController (self, elem):
    c = foam.openflow.types.Controller()
    c.type = elem.get("type")
    c.url = elem.get("url")
    return c

  def __parseDatav3 (self, dom):
    flog = logging.getLogger('foam')
    sliver_dom = dom.find('{%s}sliver' % (OFNSv3))  
    if sliver_dom is None:
      flog.exception("No Sliver Tag")
      #raise NoSliverTag()
      raise Exception()
    self.setEmail(sliver_dom.get("email", None))
    self.setDescription(sliver_dom.get("description", None))
    self.__ref = sliver_dom.get("ref", None)

    controller_elems = sliver_dom.findall('{%s}controller' % (OFNSv3))
    if controller_elems is None:
      raise NoControllersDefined()
    for elem in controller_elems:
      self.addController(self.makeController(elem))

    groups = sliver_dom.findall('{%s}group' % (OFNSv3))
    for grp in groups:
      dplist = []
      grpname = grp.get("name")
      if grpname is None:
        raise NoGroupName()
      datapaths = grp.findall('{%s}datapath' % (OFNSv3))
      for dp in datapaths:
#        try:
        dplist.append(GENIDatapath(dp))
#        except UnmanagedComponent, e:
#          continue
      self.addGroup(grpname, dplist)

    
    matches = sliver_dom.findall('{%s}match' % (OFNSv3))
    for flowspec in matches:
      fs = self.parseFlowSpec(flowspec, OFNSv3)
      self.addFlowSpec(fs)
        
    vlinks = sliver_dom.findall('{%s}vlink' % (OFNSv3))
    for virtuallink in vlinks:
      vl = self.parseVirtualLink(virtuallink, OFNSv3)
      self.addVirtualLink(vl)

  def validate (self):
    super(GENISliver, self).validate()

    if self.getEmail() is None:
      raise NoExperimenterEmail()

    for fs in self.getFlowspecs():
      for dltype in fs.getEtherTypes():
        if dltype == "0x88cc":
          raise IllegalEthertype(dltype)

  def getExpiration (self):
    return GeniDB.getSliverExpiration(self.__urn)

  def emailCheck (self, now):
    tdw = datetime.timedelta(7)
    tdd = datetime.timedelta(hours=30)

    exp = self.getExpiration()
    if not self.getEmailStatus("day"):
      if now + tdd > exp:
        foam.task.emailSliverExpDay(GeniDB.getSliverData(self.__urn, True))
        self.setEmailStatus("day")
        self.setEmailStatus("week")
        self.store()
        return (self.__urn, 1)
    if not self.getEmailStatus("week"):
      if now + tdw > exp:
        foam.task.emailSliverExpWeek(GeniDB.getSliverData(self.__urn, True))
        self.setEmailStatus("week")
        self.store()
        return (self.__urn, 2)
    return (self.__urn, 0)

  def getDataDict (self, detail = True):
    obj = super(GENISliver, self).getDataDict(detail)

    obj["user"] = self.__user_urn
    obj["sliver_urn"] = self.__urn
    obj["ref"] = self.__ref
    obj["pend_reason"] = self.__pend_reason

    return obj

  def setSliverURN (self, sliver_urn):
    self.__urn = sliver_urn

  def setUserURN (self, user_urn):
    self.__user_urn = user_urn

  def setUserEmail (self, email, overwrite=False):
    if overwrite:
      self.setEmail(email)
    elif self.getEmail() is None:
      self.setEmail(email)

  def generateURN (self, slice_urn):
    self.__slice_urn = slice_urn
    return "%s:%s" % (slice_urn, self.getUUID())
    
  def parseVirtualLink (self, elem, ns):
    vl = VirtualLink()
    
    hopsdom = elem.find("{%s}hops" % (ns))
    if hopsdom is None:
      raise NoHopsTag(elem)
      
    #TODO: put the "use-group" stuff here
    
    linkstr = ""
    hops = hopsdom.findall('{%s}hop' % (ns))
    for hop in hops:
      hopstr = hop.get("link").strip()
      if hop.get("index").strip() is not "1": 
        linkstr += ","
      linkstr += hopstr     
    vl.addVLinkFromString(linkstr)  
    return vl
  
  def parseFlowSpec (self, elem, ns):
    fs = FlowSpec()

    packetdom = elem.find("{%s}packet" % (ns))
    if packetdom is None:
      raise NoPacketTag(elem)

    use_groups = elem.findall('{%s}use-group' % (ns))
    for grp in use_groups:
      grpname = grp.get("name")
      datapaths = self.getGroupDatapaths(grpname)
      for dp in datapaths:
        fs.bindDatapath(dp)
    
    nodes = elem.findall('{%s}datapath' % (ns))
    for dpnode in nodes:
      dp = GENIDatapath(dpnode)
      fs.bindDatapath(dp)

    nodes = packetdom.findall('{%s}dl_src' % (ns))
    for dls in nodes:
      macstr = dls.get("value").strip()
      fs.addDlSrcFromString(macstr)

    nodes = packetdom.findall('{%s}dl_dst' % (ns))
    for dld in nodes:
      macstr = dld.get("value").strip()
      fs.addDlDstFromString(macstr)

    nodes = packetdom.findall('{%s}dl_type' % (ns))
    for dlt in nodes:
      dltstr = dlt.get("value").strip()
      fs.addDlTypeFromString(dltstr)

    nodes = packetdom.findall('{%s}dl_vlan' % (ns))
    for elem in nodes:
      vlidstr = elem.get("value").strip()
      fs.addVlanIDFromString(vlidstr)

    nodes = packetdom.findall('{%s}nw_src' % (ns))
    for elem in nodes:
      nwstr = elem.get("value").strip()
      fs.addNwSrcFromString(nwstr)

    nodes = packetdom.findall('{%s}nw_dst' % (ns))
    for elem in nodes:
      nwstr = elem.get("value").strip()
      fs.addNwDstFromString(nwstr)

    nodes = packetdom.findall('{%s}nw_proto' % (ns))
    for elem in nodes:
      nwproto = elem.get("value").strip()
      fs.addNwProtoFromString(nwproto)

    nodes = packetdom.findall('{%s}tp_src' % (ns))
    for elem in nodes:
      tpsrc = elem.get("value").strip()
      fs.addTpSrcFromString(tpsrc)

    nodes = packetdom.findall('{%s}tp_dst' % (ns))
    for elem in nodes:
      tpdst = elem.get("value").strip()
      fs.addTpDstFromString(tpdst)
  
    return fs

    

