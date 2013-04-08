from lxml import etree as ET
import uuid
import datetime
import hashlib
import logging
import logging.handlers
import os.path
from StringIO import StringIO

from openflow.optin_manager.xmlrpc_server.models import CallBackServerProxy, FVServerProxy
from openflow.optin_manager.sfa.OFShell import OFShell


OFNSv3 = "/opt/foamofelia/ofelia/foam/schemas/"
OFNSv4 = "/opt/foamofelia/ofelia/foam/schemas/"
PGNS = "/opt/foamofelia/ofelia/foam/schemas/"
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


  flow_visor = FVServerProxy.objects.all()[0]
  devices = OFShell().get_switches(flow_visor)
  links = OFShell().get_links(flow_visor)
 
  #links = FV.getLinkList()
  #devices =FV.getDeviceList()
  #db_devices = GeniDB.getDeviceSet()
  #GeniDB.refreshDevices(devices)

  for dpid in devices:
    #db_devices.discard(dpid)
    addAdDevice(rspec, dpid)

  #for dpid in db_devices:
  #  addAdDevice(rspec, dpid, False)

#getLinks START    
  for link in links:
    addAdLink(rspec, link)
#getLinks END 

  xml = StringIO()
  ET.ElementTree(rspec).write(xml)
  return xml.getvalue()


def addAdDevice (rspec, dpid, active=True):
  switch_urn = generateSwitchComponentID(dpid['dpid'])

  od = ET.SubElement(rspec, "{%s}datapath" % ('optin_manager'))
  od.attrib["component_id"] = switch_urn
  od.attrib["component_manager_id"] = "urn:publicid:IDN+openflow:foam:%s+authority+am" % ('i2cat.ocf.of')
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
  return "urn:publicid:IDN+openflow:foam:%s+datapath+%s" % (tag, dpid)




a = getAdvertisement()
print a
