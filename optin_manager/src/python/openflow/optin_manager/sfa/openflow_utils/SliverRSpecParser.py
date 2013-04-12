class GENIDatapath():
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





class GENISliver:
  def __init__ (self, dom):

    self.__urn = None
    self.__slice_urn = None
    self.__user_urn = None
    self.__ref = None
    self.__pend_reason = None

    if dom:
      self.__parseDatav3(dom)

  def setPendReason (self, reason):
    self.__pend_reason = reason

  def getURN (self):
    return self.__urn

  def getSliceURN (self):
    return self.__slice_urn

  def getUserURN (self):
    return self.__user_urn

  def __parseDatav3 (self, dom):
    sliver_dom = dom.find('{%s}sliver' % (OFNSv3))  
    if sliver_dom is None:
      raise Exception ("NoSliverTag")
    self.setEmail(sliver_dom.get("email", None))
    self.setDescription(sliver_dom.get("description", None))
    self.__ref = sliver_dom.get("ref", None)

    controller_elems = sliver_dom.findall('{%s}controller' % (OFNSv3))
    if controller_elems is None:
      raise Exception ("NoControllersDefined")
    for elem in controller_elems:
      self.addController(self.makeController(elem))

    groups = sliver_dom.findall('{%s}group' % (OFNSv3))
    for grp in groups:
      dplist = []
      grpname = grp.get("name")
      if grpname is None:
        raise Exception("NoGroupName")
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

  def getDataDict (self, detail = True):
    obj = dict()
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

