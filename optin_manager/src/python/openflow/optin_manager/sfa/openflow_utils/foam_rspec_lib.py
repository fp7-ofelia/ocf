from lxml import etree as ET
import uuid
import datetime
import hashlib
import logging
import logging.handlers
import os.path
from StringIO import StringIO

from openflow.optin_manager.xmlrpc_server.models import CallBackServerProxy, FVServerProxy
#from openflow.optin_manager.sfa.drivers.OFShell import OFShell

'''
Functions used in FOAM and adapted to optin in order to make the minimal changes to add the SFA plugin to FOAM
'''


OFNSv3 = "https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas"
OFNSv4 = "https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas"
PGNS = "https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas"
XSNS = "http://www.w3.org/2001/XMLSchema-instance"

def getAdvertisement (nodes):
  NSMAP = {None: "%s" % (PGNS),
          "xs" : "%s" % (XSNS),
          "openflow" : "%s" % (OFNSv3)}

  rspec = ET.Element("rspec", nsmap = NSMAP)
  rspec.attrib["{%s}schemaLocation" % (XSNS)] = PGNS + " " \
              "http://www.geni.net/resources/rspec/3/ad.xsd " + \
              OFNSv3 + " " \
              "http://www.geni.net/resources/rspec/ext/openflow/3/of-ad.xsd"
  rspec.attrib["type"] = "advertisement"


  devices = nodes['switches']#OFShell().get_switches(flow_visor)
  links = nodes['links']#OFShell().get_links(flow_visor)
 
  #links = FV.getLinkList()
  #devices =FV.getDeviceList()
  #db_devices = GeniDB.getDeviceSet()
  #GeniDB.refreshDevices(devices)
  if devices:
    for dpid in devices:
      #db_devices.discard(dpid)
      addAdDevice(rspec, dpid)

  #for dpid in db_devices:
  #  addAdDevice(rspec, dpid, False)

#getLinks START
  if links:    
    for link in links:
      addAdLink(rspec, link)
#getLinks END 

  xml = StringIO()
  element = ET.ElementTree(rspec)
  return rspec


def addAdDevice (rspec, dpid, active=True):
  switch_urn = generateSwitchComponentID(dpid['dpid'])

  od = ET.SubElement(rspec, "{%s}datapath" % (OFNSv3))
  od.attrib["component_id"] = switch_urn
  od.attrib["component_manager_id"] = "urn:publicid:IDN+openflow:optin_manager:%s+authority+am" % ('i2cat.ocf.of')
  od.attrib["dpid"] = dpid['dpid']

  #locdata = GeniDB.getLocationData(dpid, switch_urn)
  #if locdata:
  #  ET.SubElement(od, "{%s}location" % (OFNSv3), country=locdata.country, latitude=locdata.lat, longitude=locdata.long)

  #attachments = TopoDB.getDPIDAttachments(dpid)

  if active:
    ports = dpid['ports']#FV.getDevicePorts(dpid)
    for port in ports:
      p = ET.SubElement(od, "{%s}port" % (OFNSv3), num=str(port['port_num']), name=port['port_name'])
      #for info in attachments.setdefault(port.name, []):
      #  a = ET.SubElement(p, "{%s}attachment" % (OFNSv3))
      #  a.attrib["remote_component_id"] = info.remote_component_id
      #  a.attrib["remote_port"] = info.remote_port
      #  a.attrib["desc"] = info.desc


def addAdLink (rspec, link):
  od = ET.SubElement(rspec, "{%s}link" % (OFNSv3))
  od.attrib["srcDPID"] = link['src']['dpid']#link["srcDPID"]
  od.attrib["srcPort"] = link['src']['port']#link["srcPort"]
  od.attrib["dstDPID"] = link['dst']['dpid']#link["dstDPID"]
  od.attrib["dstPort"] = link['dst']['port']#link["dstPort"]


def generateSwitchComponentID (dpid, tag = None):
  if tag is None:
    tag = 'ocf_of'
  return "urn:publicid:IDN+openflow:optin_manager:%s+datapath+%s" % (tag, dpid)


def getManifest(slivers, slice_leaf):
  NSMAP = {None: "%s" % (PGNS),
          "xs" : "%s" % (XSNS),
          "openflow" : "%s" % (OFNSv3)}

  rspec = ET.Element("rspec", nsmap = NSMAP)
  rspec.attrib["{%s}schemaLocation" % (XSNS)] = PGNS + " " \
              "http://www.geni.net/resources/rspec/3/ad.xsd " + \
              OFNSv3 + " " \
              "http://www.geni.net/resources/rspec/ext/openflow/3/of-ad.xsd"
  rspec.attrib["type"] = "manifest"
  if len(slivers) == 0:
      od = ET.SubElement(rspec, "sliver")
      od.attrib["slice"] = "No sliver/s requested"

  for sliver in slivers:
      od = ET.SubElement(rspec, "sliver")
      od.attrib["slice"] = slice_leaf
      od.attrib["description"] = sliver['description']
      od.attrib["email"] = sliver['email']
      od.attrib["status"] = 'Pending to approval'

   
  return rspec
