#approval script refactored for OFELIA needs by Vasileios Kotronis
#in the following I use the prefix "of" to distuingish between the 
#foam's internal approval script and the current one (tailored for OFELIA)

import logging
import uuid

from foamext.IPy import IP, _prefixlenToNetmask
from foam.geni.db import GeniDB
from foam.core.exception import CoreException
from foam.core.log import KeyAdapter
from foam.openflow.types import Port
from foam.geni.approval import UnknownApprovalMode, ApprovalFailure, \
															 UncoveredFlowspecs, ConflictingPorts, \
															 UnboundedDatapath, VLANPresence,			 \
															 NoDatapaths, PortAlyzer, PortGroup, 	 \
															 IllegalPortGroupValue, IllegalUserURNValue, \
															 updatePortGroups, updateUserURNs, setMode
from foam.flowclashdetection.flowfieldtrees import MACIValTree, VLANIValTree, \
																									 IPSubnetIValTree, TPPortIValTree
from foam.ethzlegacyoptinstuff.legacyoptin.flowspaceutils import int_to_dotted_ip, dotted_ip_to_int, \
																										 mac_to_int, int_to_mac

NEVER = 0
ALWAYS = 1
RULES = 2

def of_rebuildDB ():
	of_AppData.rebuild()
	
def of_analyzeForApproval (sliver):
	flog = logging.getLogger("foam")
  
	if of_AppData.approveUser(sliver.getUserURN()):
		return True

	try:
		of_AppData.validateSliver(sliver)
		return True
	except (ApprovalFailure, UncoveredFlowspecs), e:
		flog.info("Sliver (%s) pended: %s" % (sliver.getURN(), str(e)))
		sliver.setPendReason(str(e))
		sliver.store()
		return False
	except Exception, e:
		flog.exception("[Approval] Sliver (%s) pended because of untrapped exception" % (sliver.getURN()))
	
	
class MACConflict(ApprovalFailure):
	def __init__ (self, mac):
		super(MACConflict, self).__init__()
		self.mac = mac
	def __str__ (self):
		return "MAC Address (%s) is already reserved by another sliver." % (self.mac)
		
class IvalMACConflict(ApprovalFailure):
	def __init__ (self, stmac, endmac):
		super(IvalMACConflict, self).__init__()
		self.stmac = stmac
		self.endmac = endmac
	def __str__ (self):
		return "MAC Address Interval [%s-%s] clashes with another sliver." % (self.stmac, self.endmac)

class EtherTypeConflict(ApprovalFailure):
	def __init__ (self, dltype):
		super(EtherTypeConflict, self).__init__()
		self.dltype = dltype
	def __str__ (self):
		return "Ethertype (%s) is already reserved by another sliver." % (self.dltype)

class VLANConflict(ApprovalFailure):
	def __init__ (self, vlanid):
		super(VLANConflict, self).__init__()
		self.vlanid = vlanid
	def __str__ (self):
		return "VLAN (%s) is already reserved by another sliver." % (self.vlanid)
		
class IvalVLANConflict(ApprovalFailure):
	def __init__ (self, stvlanid, endvlanid):
		super(IvalVLANConflict, self).__init__()
		self.stvlanid = stvlanid
		self.endvlanid = endvlanid
	def __str__ (self):
		return "VLAN Interval [%s-%s] clashes with another sliver." % (self.stvlanid, self.endvlanid)
		
class IPSubnetConflict(ApprovalFailure):
	def __init__ (self, subnet):
		super(IPSubnetConflict, self).__init__()
		self.subnet = subnet
	def __str__ (self):
		return "IP Subnet (%s) is already reserved by another sliver." % (str(self.subnet))
		
class IvalIPSubnetConflict(ApprovalFailure):
	def __init__ (self, stIP, endIP):
		super(IvalIPSubnetConflict, self).__init__()
		self.subnet = subnet
	def __str__ (self):
		return "IP Subnet (%s) clashes with another sliver." % (str(self.subnet))
		
class TPPortConflict(ApprovalFailure):
	def __init__ (self, tpport):
		super(TPPortConflict, self).__init__()
		self.tpport = tpport
	def __str__ (self):
		return "Transport protocol port (%s) is already reserved by another sliver." % (self.tpport)
		
class IvalTPPortConflict(ApprovalFailure):
	def __init__ (self, sttpport, endtpport):
		super(IvalTPPortConflict, self).__init__()
		self.sttpport = sttpport
		self.endtpport = endtpport
	def __str__ (self):
		return "Transport protocol port Interval [%s-$s] clashes with another sliver." % (self.sttpport, self.endtpport)
		
		
class of_ApprovalData(object):
	def __init__ (self, slivers = None):
		self._log = KeyAdapter("OFELIA Approval", logging.getLogger("foam"))
		self._initCore()
		self._build(slivers)
	
	def _build (self, slivers):
		self._loadSlivers(slivers)
		self._loadPortGroups()
		self._loadUserURNs()
		self._buildIValTrees(slivers)
		
	def _buildIValTrees(self, slivers): #dl type and NW proto not needed to ne handled by a tree structure
		MACTree = MACIValTree([])
		VLANTree = VLANIValTree([])
		IPSubnetTree = IPSubnetIValTree([])
		TPPortTree = TPPortIValTree([])
		
		for sliv in slivers:
			fspecs = sliv.getFlowspecs()
			for fs in fspecs:
					
				#build MAC tree from pool of MACS
				newInterval = True
				previntmac = None
				for mac in sorted(fs.getMACs()):
					intmac = mac_to_int(mac)
					if newInterval == True:	#new interval encountered
						MACstart = intmac
						MACstop = intmac
					else:
						if previntmac != None: 
							if (intmac - previntmac) == 1:	#still within the interval
								MACstop = intmac
								newInterval = False
							else:	#register the interval
								MACTree.addIVal(MACTree.root, MACstart, MACstop, sliv.getURN())
								newInterval = True
					previntmac = intmac
				
				#build VLAN tree from pool of VLANs
				newInterval = True
				previntvlanid = None
				for vlanid in sorted(fs.getVLANs()):
					intvlanid = int(vlanid)
					if newInterval == True:	#new interval encountered
						VLANstart = intvlanid
						VLANstop = intvlanid
					else:
						if previntvlanid != None: 
							if (intvlanid - previntvlanid) == 1:	#still within the interval
								VLANstop = intvlanid
								newInterval = False
							else:	#register the interval
								VLANTree.addIVal(VLANTree.root, VLANstart, VLANstop, sliv.getURN())
								newInterval = True
					previntvlanid = intvlanid
					
				#build IP address tree from pool of IP subnets (first make them intervals)
				for IPSub in fs.getIPSubnets():
					IPSubparsed = self.parseSubnet(IPSub)
					IPSubLen = IP(IPSubparsed).len()
					IPstart = int(IP(IPSubparsed[0]).strDec())
					IPstop = IPstart + IPSubLen - 1
					IPSubnetTree.addIVal(IPSubnetTree.root, IPstart, IPstop, sliv.getURN())
				
				#build TP port tree from pool of TP ports
				newInterval = True
				previnttpport = None
				for tpport in sorted(fs.getTPPorts()):
					inttpport = int(tpport)
					if newInterval == True:	#new interval encountered
						TPPortstart = inttpport
						TPPortstop = inttpport
					else:
						if previnttpport != None: 
							if (inttpport - prevtpport) == 1:	#still within the interval
								TPPortstop = tpport
								newInterval = False
							else:	#register the interval
								TPPortTree.addIVal(TPPortTree.root, TPPortstart, TPPortstop, sliv.getURN())
								newInterval = True
					previnttpport = inttpport
		
		self._macivtree = MACTree	 
		self._vlanivtree = VLANTree
		self._subnetivtree = IPSubnetTree
		self._tpportivtree = TPPortTree
		
	def _initCore (self):
		self._macs = set()
		self._macivtree = set()
		self._ethertypes = set()
		self._vlans = set()
		self._vlanivtree = set()
		self._subnets = set()
		self._subnetivtree = set()
		self._nwprotos = set()
		self._tpports = set()
		self._tpportivtree = set()
		self._portgroups = {}
		self._urns = set()
	
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
	
	def approveUser (self, urn):
		if urn in self._urns:
			return True
		else:
			return False
	
	def parseSubnet (self, netstr):
		(i,pl) = netstr.split("/")
		net = IP(i)
		nm = IP(_prefixlenToNetmask(int(pl), 4))
		net.make_net(nm)
		return net
	
	def validateSliver (self, sliver):
		if not ConfigDB.getConfigItemByKey("geni.openflow.analysis-engine").getValue():
			return

		fspecs = sliver.getFlowspecs()
		uncovered_fs = []
		for fs in fspecs:
			covered = False
			
			if fs.hasVLANs():
				#check VLAN clash
				covered = True
				newInterval = True
				previntvlanid = None
				for vlanid in sorted(fs.getVLANs()):
					intvlanid = int(vlanid)
					if newInterval == True:	#new interval encountered
						VLANstart = intvlanid
						VLANstop = intvlanid
					else:
						if previntvlanid != None: 
							if (intvlanid - previntvlanid) == 1:	#still within the interval
								VLANstop = intvlanid
								newInterval = False
							else:	#find overlap if exists
								ovList = self._vlanivtree.findOverlapIVal(self._vlanivtree.root, VLANstart, VLANstop, [])
								if ovList != []:
									raise IValVLANConflict(VLANstart, VLANstop)
								newInterval = True
					previntvlanid = intvlanid
			
			#check MAC clash
			newInterval = True
			previntmac = None
			for mac in sorted(fs.getMACs()):
				covered = True
				intmac = mac_to_int(mac)
				if newInterval == True:	#new interval encountered
					MACstart = intmac
					MACstop = intmac
				else:
					if previntmac != None: 
						if (intmac - previntmac) == 1:	#still within the interval
							MACstop = intmac
							newInterval = False
						else:	#find overlap if exists
							ovList = self._macivtree.findOverlapIVal(self._macivtree.root, MACstart, MACstop, [])
							if ovList != []:
								raise IvalMACConflict(MACstart, MACstop)
							newInterval = True
				previntmac = intmac
				
			#check dl type clash
			for dltype in fs.getEtherTypes():
				covered = True
				if dltype == "0x806" or dltype == "0x800":
					continue
				if dltype in self._ethertypes:
					raise EtherTypeConflict(dltype)
				
			#check IP subnet clash
			for IPSub in fs.getIPSubnets():
				covered = True
				IPsubparsed = self.parseSubnet(IPSub)
				IPSubLen = IP(IPSubparsed).len()
				IPstart = int(IP(IPSubparsed[0]).strDec())
				IPstop = IPstart + IPSubLen - 1
				ovList = self._subnetivtree.findOverlapIVal(self._subnetivtree.root, IPstart, IPstop, [])
				if ovList != []:
					raise IvalIPSubnetConflict(IP(IPsub))
					
			#check TP port clash
			newInterval = True
			previnttpport = None
			for tpport in sorted(fs.getTPPorts()):
				covered = True
				inttpport = int(tpport)
				if newInterval == True:	#new interval encountered
					TPPortstart = inttpport
					TPPortstop = inttpport
				else:
					if previnttpport != None: 
						if (inttpport - prevtpport) == 1:	#still within the interval
							TPPortstop = tpport
							newInterval = False
						else:	#find overlap if exists
							ovList = self._tpportivtree.findOverlapIVal(self._tpportivtree.root, TPPortstart, TPPortstop, [])
							if ovList != []:
								raise IvalTPPortConflict(TPPortstart, TPPortstop)
							newInterval = True
				previnttpport = inttpport
					
			has_dps = False
			dps = fs.getDatapaths()
			if not dps:
				raise NoDatapaths(fs)

			pl = PortAlyzer(self._portgroups)
			pl.validate(dps)
		
			if not covered:
				uncovered_fs.append(fs)

		if uncovered_fs:
			raise UncoveredFlowspecs(uncovered_fs)
			
	def addSliver (self, sliver):
		fspecs = sliver.getFlowspecs()
		
		for fs in fspecs:
			#add macs old style
			for mac in fs.getMACs():
				self._macs.add(mac)
			#add intervalized macs (new style)
			newInterval = True
			previntmac = None
			for mac in sorted(fs.getMACs()):
				intmac = mac_to_int(mac)
				if newInterval == True:	#new interval encountered
					MACstart = intmac
					MACstop = intmac
				else:
					if previntmac != None: 
						if (intmac - previntmac) == 1:	#still within the interval
							MACstop = intmac
							newInterval = False
						else:	#register the interval
							self._macivtree.addIVal(self._macivtree.root, MACstart, MACstop, sliver.getURN())
							newInterval = True
				previntmac = intmac
				
				#add dltypes old style
				for dltype in fs.getEtherTypes():
					if ((dltype == "0x806") or (dltype == "0x800")):
						continue
					self._ethertypes.add(dltype)
				
				#add vlans old style
				for vlanid in fs.getVLANs():
					self._vlans.add(vlanid)
				#add intervalized vlans (new style)
				newInterval = True
				previntvlanid = None
				for vlanid in sorted(fs.getVLANs()):
					intvlanid = int(vlanid)
					if newInterval == True:	#new interval encountered
						VLANstart = intvlanid
						VLANstop = intvlanid
					else:
						if previntvlanid != None: 
							if (intvlanid - previntvlanid) == 1:	#still within the interval
								VLANstop = intvlanid
								newInterval = False
							else:	#register the interval
								self._vlanivtree.addIVal(self._vlanivtree.root, VLANstart, VLANstop, sliver.getURN())
								newInterval = True
					previntvlanid = intvlanid
				
				#add IP subnets old style
				for subnet in fs.getIPSubnets():
					net = IP(subnet)
					self._subnets.add(net)
				#add intervalized IP subnets
				for IPSub in fs.getIPSubnets():
					IPsubparsed = self.parseSubnet(IPSub)
					IPSubLen = IP(IPSubparsed).len()
					IPstart = int(IP(IPSubparsed[0]).strDec())
					IPstop = IPstart + IPSubLen - 1
					self._subnetivtree.addIVal(self._subnetivtree.root, IPstart, IPstop, sliver.getURN())
					
				#add NW protos old style
				for nwprot in fs.getNWProtos():
					self._nwprotos.add(nwprot)
					
				#add TP ports old style
				for tpp in fs.getTPPorts():
					self._tpports.add(tpp)
				#add intervalized TP ports (new style)
				newInterval = True
				previnttpport = None
				for tpport in sorted(fs.getTPPorts()):
					inttpport = int(tpport)
					if newInterval == True:	#new interval encountered
						TPPortstart = inttpport
						TPPortstop = inttpport
					else:
						if previnttpport != None: 
							if (inttpport - prevtpport) == 1:	#still within the interval
								TPPortstop = tpport
								newInterval = False
							else:	#register the interval
								self._tpportivtree.addIVal(self._tpportivtree.root, TPPortstart, TPPortstop, sliver.getURN())
								newInterval = True
					previnttpport = inttpport
				
	def iterMACs (self):
		for x in self._macs: 
			yield x

	def iterEthertypes (self):
		for x in self._ethertypes: 
			yield x
	
	def iterVLANs (self):
		for x in self._vlans: 
			yield x
		
	def iterSubnets (self):
		for x in self._subnets: 
			yield x
		
	def iterNWProtos (self):
		for x in self._nwprotos: 
			yield x
	
	def iterTPPorts (self):
		for x in self._tpports:
			yield x
		

from foam.core.configdb import ConfigDB

of_AppData = of_ApprovalData(GeniDB.getSliverList(False, True, True))
