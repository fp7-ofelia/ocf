# Copyright (c) 2012  Nick Bastin

import logging
import uuid

from foamext.IPy import IP
from foamext import IPy
from foam.geni.db import GeniDB
from foam.core.exception import CoreException
from foam.core.log import KeyAdapter
from foam.openflow.types import Port

NEVER = 0
ALWAYS = 1
RULES = 2

def rebuildDB ():
  AppData.rebuild()

def analyzeForApproval (sliver):
  flog = logging.getLogger("foam")
  
  if AppData.approveUser(sliver.getUserURN()):
    return True

  try:
    AppData.validateSliver(sliver)
    return True
  except (ApprovalFailure, UncoveredFlowspecs), e:
    flog.info("Sliver (%s) pended: %s" % (sliver.getURN(), str(e)))
    sliver.setPendReason(str(e))
    sliver.store()
    return False
  except Exception, e:
    flog.exception("[Approval] Sliver (%s) pended because of untrapped exception" % (sliver.getURN()))
  
class UnknownApprovalMode(CoreException):
  def __init__ (self, val):
    super(CoreException, self).__init__()
    self.val = val
  def __str__ (self):
    return "Unknown approval mode: %s" % (str(val))

class ApprovalFailure(CoreException):
  def __init__ (self):
    super(ApprovalFailure, self).__init__()

class MACConflict(ApprovalFailure):
  def __init__ (self, mac):
    super(MACConflict, self).__init__()
    self.mac = mac
  def __str__ (self):
    return "MAC Address (%s) is already reserved by another sliver." % (self.mac)

class EtherTypeConflict(ApprovalFailure):
  def __init__ (self, dltype):
    super(EtherTypeConflict, self).__init__()
    self.dltype = dltype
  def __str__ (self):
    return "Ethertype (%s) is already reserved by another sliver." % (self.dltype)

class IPSubnetConflict(ApprovalFailure):
  def __init__ (self, subnet):
    super(IPSubnetConflict, self).__init__()
    self.subnet = subnet
  def __str__ (self):
    return "IP Subnet (%s) is already reserved by another sliver." % (str(self.subnet))

class UncoveredFlowspecs(CoreException):
  def __init__ (self, flowspecs):
    super(UncoveredFlowspecs, self).__init__()
    self.flowspecs = flowspecs
  def __str__ (self):
    return "Flowspecs found that can't be handled by overlap engine."

class ConflictingPorts(ApprovalFailure):
  def __init__ (self, portgroup):
    super(ConflictingPorts, self).__init__()
    self.pg = portgroup
  def __str__ (self):
    return "Ports requested which overlap administrator-defined port group (%s)" % (self.pg.uuid)

class UnboundedDatapath(CoreException):
  def __init__ (self, dpobj):
    super(UnboundedDatapath, self).__init__()
    self.dpobj = dpobj
  def __str__ (self):
    return "Request for unbounded datapath (%s) with portgroups defined" % (self.dpobj.dpid)

class VLANPresence(ApprovalFailure):
  def __init__ (self, fs):
    super(VLANPresence, self).__init__()
    self.fs = fs
  def __str__ (self):
    return "Request has underspecified VLAN requests"

'''
class VLANConflictError(ApprovalFailure):
  def __init__ (self, vid):
    super(VLANConflictError, self).__init__()
    self.vid = vid
  def __str__ (self):
    return "VLAN ID (%d) is already reserved by another sliver." % (self.vid)

class ReservedVLANError(ApprovalFailure):
  def __init__ (self, vid):
    super(ReservedVLANError, self).__init__()
    self.vid = vid
  def __str__ (self):
    return "VLAN ID (%d) is reserved by the administrator." % (self.vid)
'''
    
class NoDatapaths(ApprovalFailure):
  def __init__ (self, fs):
    super(NoDatapaths, self).__init__()
    self.fs = fs
  def __str__ (self):
    return "Request for all datapaths with portgroups defined"


class PortAlyzer(object):
  def __init__ (self, pgs):
    self._prepare(pgs)

  def _prepare (self, pgs):
    tmp = {}
    for k,v in pgs.iteritems():
      v.count = 0
      tmp[k] = v
    self._pgs = tmp

  def validate (self, dps):
    if not self._pgs:
      return
    for dpobj in dps:
      if dpobj.ports:
        for pg in self._pgs.itervalues():
          for port in dpobj.ports:
            if port in pg.ports:
              pg.count += 1
      else:
        raise UnboundedDatapath(dpobj)
    for pg in self._pgs.itervalues():
      if pg.count > 1:
        raise ConflictingPorts(pg)


class PortGroup(object):
  def __init__ (self):
    self.uuid = uuid.uuid4()
    self.name = None
    self.desc = None
    self.ports = set()

  def __json__ (self):
    return { "id" : str(self.uuid), "name" : self.name, "desc" : self.desc,
             "ports" : [x for x in self.ports] }

  def addPort (self, dpid, num):
    p = Port()
    p.dpid = dpid
    p.num = num
    self.ports.add(p)
    AppData._updatePGData()

  def removePort (self, dpid, num):
    p = Port()
    p.dpid = dpid
    p.num = num
    self.ports.remove(p)
    AppData._updatePGData()


class ApprovalData(object):
  def __init__ (self, slivers = None):
    self._log = KeyAdapter("GENI Approval", logging.getLogger("foam"))
    self._initCore()
    self._build(slivers)

  def _build (self, slivers):
    self._loadSlivers(slivers)
    self._loadPortGroups()
    self._loadUserURNs()
    #self._loadAdminVLANs()

  def _initCore (self):
    self._subnets = set()
    self._macs = set()
    self._ethertypes = set()
    self._portgroups = {}
    self._urns = set()
    #self._vlans = set()
    #self._admin_vlans = set()
    #self._shared_vlans = set()
    
  def _loadSlivers (self, slivers):
    for sliver in slivers:
      self.addSliver(sliver)

  def _loadPortGroups (self):
    groups = ConfigDB.getConfigItemByKey("geni.openflow.portgroups").getValue()
    if groups is None:
      return
    self._portgroups = groups

  def _updatePGData (self):
    groups = ConfigDB.getConfigItemByKey("geni.openflow.portgroups").write(self._portgroups)

  def rebuild (self):
    self._log.info("Rebuilding approval database")
    self._initCore()
    self._build(GeniDB.getSliverList(False, True, True))

  def _loadUserURNs (self):
    urns = ConfigDB.getConfigItemByKey("geni.approval.user-urns").getValue()
    if urns is None:
      return
    for urn in urns:
      self._urns.add(urn)

  '''
  def _loadAdminVLANs (self):
    vlans = ConfigDB.getConfigItemByKey("geni.approval.admin-vlans").getValue()
    if vlans is not None:
      self._admin_vlans = vlans
    vlans = ConfigDB.getConfigItemByKey("geni.approval.shared-vlans").getValue()
    if vlans is not None:
      self._shared_vlans = vlans    
  '''
  
  def createPortGroup (self, name, desc):
    pg = PortGroup()
    pg.name = name
    pg.desc = desc
    self._portgroups[str(pg.uuid)] = pg
    self._updatePGData()
    return pg

  def getPortGroup (self, pgid):
    return self._portgroups[pgid]

  def getPortGroups (self):
    return self._portgroups

  def addUserURN (self, urn, user = None):
    item = ConfigDB.getConfigItemByKey("geni.approval.user-urns")
    if user:
      user.assertPrivilege(item.getRWAttrs())
    self._urns.add(urn)
    item.write(self._urns)

  def removeUserURN (self, urn, user = None):
    item = ConfigDB.getConfigItemByKey("geni.approval.user-urns")
    if user:
      user.assertPrivilege(item.getRWAttrs())
    self._urns.discard(urn)
    item.write(self._urns)
    
  '''
  def addAdminVLAN (self, vlan, user = None):
    item = ConfigDB.getConfigItemByKey("geni.approval.admin-vlans")
    if user:
      user.assertPrivilege(item.getRWAttrs())
    self._admin_vlans.add(vlan)
    item.write(self._admin_vlans)

  def removeAdminVLAN (self, vlan, user = None):
    item = ConfigDB.getConfigItemByKey("geni.approval.admin-vlans")
    if user:
      user.assertPrivilege(item.getRWAttrs())
    self._admin_vlans.discard(vlan)
    item.write(self._admin_vlans)

  def addSharedVLAN (self, vlan, user = None):
    item = ConfigDB.getConfigItemByKey("geni.approval.shared-vlans")
    if user:
      user.assertPrivilege(item.getRWAttrs())
    self._shared_vlans.add(vlan)
    item.write(self._shared_vlans)

  def removeSharedVLAN (self, vlan, user = None):
    item = ConfigDB.getConfigItemByKey("geni.approval.shared-vlans")
    if user:
      user.assertPrivilege(item.getRWAttrs())
    self._shared_vlans.discard(vlan)
    item.write(self._shared_vlans)
  '''

  def approveUser (self, urn):
    if urn in self._urns:
      return True
    else:
      return False
      
  def parseSubnet (self, netstr):
    (i,pl) = netstr.split("/")
    net = IP(i)
    nm = IP(IPy._prefixlenToNetmask(int(pl), 4))
    net = net.make_net(nm)
    return net

  def validateSliver (self, sliver):
    if not ConfigDB.getConfigItemByKey("geni.openflow.analysis-engine").getValue():
      return

    fspecs = sliver.getFlowspecs()
    uncovered_fs = []
    for fs in fspecs:
      covered = False
      subnet_covered = False
      
      # This must come first - if you request only VLANs which are not shared, you
      # don't have to pass the rest of the rules checks (in the context of those VLANs)
      '''
      if ConfigDB.getConfigItemByKey("geni.approval.check-vlans").getValue():
        vlan_covered = None
        for vlan in fs.getVLANs():
          if vlan in self._vlans:
            raise VLANConflictError(vlan)
          if vlan in self._admin_vlans:
            raise ReservedVLANError(vlan)
          if vlan in self._shared_vlans:
            vlan_covered = False
          elif vlan_covered is None:
            vlan_covered = True
        if vlan_covered:
          continue
      elif fs.hasVLANs():
        raise VLANPresence(fs)
      '''
      
      for mac in fs.getMACs():
        covered = True
        if mac in self._macs:
          raise MACConflict(mac)
    
      for dltype in fs.getEtherTypes():
        covered = True
        if dltype == "0x806" or dltype == "0x800":
          continue
        if dltype in self._ethertypes:
          raise EtherTypeConflict(dltype)

      for subnet in fs.getIPSubnets():
        covered = True
        subnet_covered = True
        net = self.parseSubnet(subnet)
        if net in self._subnets:
          raise IPSubnetConflict(net)
        for onet in self._subnets:
          if net.overlaps(onet):
            raise IPSubnetConflict(net)

      has_dps = False
      dps = fs.getDatapaths()
      if not dps:
        raise NoDatapaths(fs)

      pl = PortAlyzer(self._portgroups)
      pl.validate(dps)
      
      if fs.hasVLANs():
        raise VLANPresence(fs)

      if not covered:
        uncovered_fs.append(fs)

    if uncovered_fs:
      raise UncoveredFlowspecs(uncovered_fs)

        
  def addSliver (self, sliver):
    fspecs = sliver.getFlowspecs()

    for fs in fspecs:
      for mac in fs.getMACs():
        self._macs.add(mac)

      for dltype in fs.getEtherTypes():
        if dltype == "0x806" or dltype == "0x800":
          continue
        self._ethertypes.add(dltype)

      for subnet in fs.getIPSubnets():
        if subnet is None:
          self._log.info("Flowspec with None subnets: %s" % (sliver))
          continue
        net = self.parseSubnet(subnet)
        #net = IP(subnet)
        self._subnets.add(net)
       
      #for vid in fs.getVLANs():
      #  self._vlans.add(vid)
    
  def iterMACs (self):
    for x in self._macs: yield x

  def iterEthertypes (self):
    for x in self._ethertypes: yield x

  def iterSubnets (self):
    for x in self._subnets: yield x

class IllegalPortGroupValue(CoreException):
  def __init__ (self, newval):
    self.val = newval
  def __str__ (self):
    return "Tried to set port groups config to illegal value: %s" % (self.val)

class IllegalUserURNValue(CoreException):
  def __init__ (self, newval):
    self.val = newval
  def __str__ (self):
    return "Tried to set User URNs config to illegal value: %s" % (self.val)
    
'''
class VLANStorageError(CoreException):
  def __init__ (self, newval):
    self.val = newval
  def __str__ (self):
    return "Tried to set admin VLANs config to illegal value: %s" % (self.val)
'''

def updatePortGroups (key, newval):
  if type(newval) is not dict:
    raise IllegalPortGroupValue()
  return newval

def updateUserURNs (key, newval):
  if type(newval) is not set:
    raise IllegalUserURNValue()
  return newval

def setMode (key, newval):
  try:
    if (type(newval) is not int):
      newval = int(newval)
  except ValueError, e:
    raise UnknownApprovalMode(newval)

  if (newval < 0) or (newval > 2):
    raise UnknownApprovalMode(newval)

  if newval == RULES:
    item = ConfigDB.getConfigItemByKey("geni.openflow.analysis-engine")
    if not item.getValue():
      item.write(True)

  return newval

from foam.core.configdb import ConfigDB

AppData = ApprovalData(GeniDB.getSliverList(False, True, True))

