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

from foam.geni.lib import generateSwitchComponentID 

'''
Functions used in FOAM and adapted to optin in order to make the minimal changes to add the SFA plugin to FOAM
'''

OFNSv3 = "https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas"
OFNSv4 = "https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas"
PGNS = "https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas"
XSNS = "http://www.w3.org/2001/XMLSchema-instance"

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
  devices =FV.getDeviceList()
  db_devices = GeniDB.getDeviceSet()
  GeniDB.refreshDevices(devices)
  if devices:
    for dpid in devices:
      db_devices.discard(dpid)
      addAdDevice(rspec, dpid)

  for dpid in db_devices:
    addAdDevice(rspec, dpid, False)

#getLinks START
  if links:
    for link in links:
      addGeniLink(rspec,link)
#getLinks END 

  xml = StringIO()
  element = ET.ElementTree(rspec)
  return rspec

def addAdDevice (rspec, dpid, active=True):
  switch_urn = generateSwitchComponentID(dpid)

  od = ET.SubElement(rspec, "{%s}datapath" % (OFNSv3))
  od.attrib["component_id"] = switch_urn
  od.attrib["component_manager_id"] = "urn:publicid:IDN+foam:%s+authority+am" % ('ocf.ofelia.i2cat.ofam')
  od.attrib["dpid"] = dpid

  #locdata = GeniDB.getLocationData(dpid, switch_urn)
  #if locdata:
  #  ET.SubElement(od, "{%s}location" % (OFNSv3), country=locdata.country, latitude=locdata.lat, longitude=locdata.long)

  #attachments = TopoDB.getDPIDAttachments(dpid)

  if active:
    ports = FV.getDevicePorts(dpid)
    for port in ports:
      p = ET.SubElement(od, "{%s}port" % (OFNSv3), num=str(port.num), name=port.name)
      #for info in attachments.setdefault(port.name, []):
      #  a = ET.SubElement(p, "{%s}attachment" % (OFNSv3))
      #  a.attrib["remote_component_id"] = info.remote_component_id
      #  a.attrib["remote_port"] = info.remote_port
      #  a.attrib["desc"] = info.desc


def addAdLink (rspec, link):
  od = ET.SubElement(rspec, "{%s}link" % (OFNSv3))
  od.attrib["srcDPID"] = link["srcDPID"]
  od.attrib["srcPort"] = link["srcPort"]
  od.attrib["dstDPID"] = link["dstDPID"]
  od.attrib["dstPort"] = link["dstPort"]

def addGeniLink(rspec, link):
  def add_dpid(od, dpid):
    dpids = ET.SubElement(od, "{%s}datapath" %(OFNSv3))
    dpids.attrib["component_id"] = "urn:publicid:IDN+foam+authority+datapath+%s" % dpid
    dpids.attrib["component_manager"] = "urn:publicid:IDN+foam+authority"
    dpids.attrib["dpid"] = dpid
  def add_port(od, port):
    ps = ET.SubElement(od, "{%s}port" %(OFNSv3))
    ps.attrib["port_num"] = link['srcPort']

  od = ET.SubElement(rspec, "{%s}link" % (OFNSv3))
  od.attrib["component_id"] = "urn:publicid:IDN+foam+authority+link+%s_%s_%s_%s" %(link["srcDPID"], link["srcPort"],link["dstDPID"],link["dstPort"])
  add_dpid(od, link["srcDPID"])
  add_port(od, link["srcPort"])
  add_dpid(od,link["dstDPID"])
  add_dpid(od,link["dstPort"])

def get_slice_details_from_slivers(slivers, slice_urn):
    for sliver in slivers:
        if sliver["slice_urn"] == slice_urn:
            return sliver
    raise Exception("Record Not Found")


