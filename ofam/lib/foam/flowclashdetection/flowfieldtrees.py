#Vasileios: implementation of the flowspace collision detection engine

import foam.geni.approval
from foam.geni.db import GeniDB
from foam.core.exception import CoreException
from foam.flowclashdetection.interval_structure import IValNode, IValTree

#check later whether extra attributes are needed per tree

class MACIValTree(IValTree):
	def __init__ (self, attr):
		super(MACIValTree, self).__init__()
		self.attr = attr
		
class VLANIValTree(IValTree):
	def __init__ (self, attr):
		super(VLANIValTree, self).__init__()
		self.attr = attr

class IPSubnetIValTree(IValTree):
	def __init__ (self, attr):
		super(IPSubnetIValTree, self).__init__()
		self.attr = attr
	
class TPPortIValTree(IValTree):
	def __init__ (self, attr):
		super(TPPortIValTree, self).__init__()
		self.attr = attr
	
#see ofeliaaproval.py for the mechanism used (at geni folder)
	

