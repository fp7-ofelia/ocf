#construct an interval tree structure
#author: Vasileios Kotronis
#based on:
#-- http://en.wikipedia.org/wiki/Interval_tree --> main source #1
#-- http://code.activestate.com/recipes/286239-binary-ordered-tree/ -->main source #2
#additional sources:
#-- http://hackmap.blogspot.ch/2008/11/python-interval-tree.html
#-- C++-->python porting from http://code.google.com/p/intervaltree/
#-- http://forrst.com/posts/Interval_Tree_implementation_in_python-e0K
#-- https://github.com/misshie/interval-tree/blob/master/lib/interval_tree.rb
#-- http://code.activestate.com/recipes/457411-an-interval-mapping-data-structure/ 

from lxml import etree

class IValNode(object):
	
	def __init__(self, low_end, high_end, value):
		self.low_end = low_end
		self.high_end = high_end
		self.max_high = 0
		self.value = value
		self.left = None
		self.right = None
		self.parent = None
		
	
class IValTree(object):
	
	def __init__(self):
		self.root = None
		self.depth = 0
		self.MIN = 0
		self.MAX = 1000000000
		
	def addIVal(self, root, start, stop, value):
		if root is None:
			root = IValNode(start, stop, value)
		else:
			root.max_high = max(root.max_high, stop)
			if start <= root.low_end:
				root.left = self.addIVal(root.left, start, stop, value)
				root.left.parent = root
			else:
				root.right = self.addIVal(root.right, start, stop, value)
				root.right.parent = root
		self.depth = self.findDepth(root)
		return root
	
	def remIVal(self, root, start, stop, value):
		iValList = self.findOverlapIVal(root, start, stop,  [])
		found_value = 0
		for i in range(len(iValList)):
			if iValList[i].value == value:
				found_value = 1
				break
		if found_value == 0:
			print "Unable to find overlapping interval with correct value!"
			return root
		node_to_remove = iValList[i]
		if node_to_remove is None:
			print "The current interval is non-existent!"
		elif node_to_remove.parent is None: #This is the current root
			print "Removing current root"
			if node_to_remove.left is None:
				if node_to_remove.right is None:	#no root, no tree
					root = None
				else:	#the first node of the right subtree will become root
					node_to_remove.right.parent = None
					root = node_to_remove.right
			else:
				if node_to_remove.right is None:	#the first node of the left subtree will become root
					node_to_remove.left.parent = None
					root = node_to_remove.left
				else: #need to rebalance the tree since both left and right subtrees not empty
					current_node = node_to_remove.right
					node_to_remove.right.parent = None
					root = node_to_remove.right	#make the initial top node of right subtree root
					while current_node.left is not None: 	#scan the right subtree until you reach the most left leaf
						current_node = current_node.left
					current_node.left = node_to_remove.left #now place there the initial left subtree
					node_to_remove.left.parent = current_node
					while current_node.parent is not None:	#now update the max_high values recursively
						current_node.max_high = max(current_node.max_high, current_node.left.max_high)	
						current_node = current_node.parent
		else: 	#The node to remove is intermediate
			print "Removing intermediate node, rebalancing tree from scratch"
			allnodes = self.findOverlapIVal(self.root, self.MIN, self.MAX, [])
			tempTree = IValTree()
			for nd in allnodes:
				if nd != node_to_remove: 
					tempTree.root = tempTree.addIVal(tempTree.root,	nd.low_end, nd.high_end, nd.value)
				else:
					print "found node to be removed, ignoring it for the formation of new tree"
			root = tempTree.root	
			self.depth = tempTree.depth

			#old code
			'''
			if node_to_remove.low_end <= node_to_remove.parent.low_end: #node is at the left
				print "node is at the left"	
				if node_to_remove.left is None:
					node_to_remove.parent.left = node_to_remove.right
				elif node_to_remove.right is None:
					node_to_remove.parent.left = node_to_remove.left
				else:				
					node_to_remove.right.parent = node_to_remove.left.right
				

				rec_node = node_to_remove.parent
				while rec_node.parent is not None:
					if rec_node.right is None:
						if rec_node.left is None:
							rec_node.max_high = 0
						else:
							rec_node.max_high = max(rec_node.left.max_high, rec_node.left.high_end)
					else:
						if rec_node_left is None:
							rec_node.max_high = max(rec_node.right.max_high,rec_node.right.high_end)
						else:
							rec_node.max_high = max(max(rec_node.left.max_high,rec_node.left.high_end), \
							max(rec_node.right.max_high,rec_node.right.high_end))
					rec_node = rec_node.parent
			else: #node is at the right
				print "node is at the right"
				node_to_remove.parent.right = node_to_remove.right
				rec_node = node_to_remove.parent
				while rec_node.parent is not None:
					if rec_node.right is None:
						if rec_node.left is None:
							rec_node.max_high = 0
						else:
							rec_node.max_high = max(rec_node.left.max_high, rec_node.left.high_end)
					else:
						if rec_node_left is None:
							rec_node.max_high = max(rec_node.right.max_high,rec_node.right.high_end)
						else:
							rec_node.max_high = max(max(rec_node.left.max_high,rec_node.left.high_end), \
							max(rec_node.right.max_high,rec_node.right.high_end))
					rec_node = rec_node.parent
		node_to_remove = None
		'''
		return root
			
	def findOverlapIVal(self, root, start, stop, cList):
		if root != None:
			if root.low_end > stop:
				cList = self.findOverlapIVal(root.left, start, stop, cList)
			elif root.high_end < start:
				if root.max_high > start:
					cList = self.findOverlapIVal(root.left, start, stop, cList)
					cList = self.findOverlapIVal(root.right, start, stop, cList)
			else:
				cList = cList + [root]
				cList = self.findOverlapIVal(root.left, start, stop, cList)
				cList = self.findOverlapIVal(root.right, start, stop, cList)
		return cList
	
	def findDepth(self, root):
		if root is None:
			return 0
		else:
			ldepth = self.findDepth(root.left)
			rdepth = self.findDepth(root.right)
			return max(ldepth, rdepth) + 1
	
	def size(self, root):
		if root is None:
			return 0
		else:
			return self.size(root.left) + 1 + self.size(root.right)
			
	def printTreeString(self, root):
		if root is None:
			pass
		else:
			print "Interval [" + str(root.low_end) + "-" + str(root.high_end) + "] : value = " + str(root.value) + \
			", maximum high end of children = " + str(root.max_high) + ", positioned at level " + str((self.depth - self.findDepth(root) + 1)),
			if root.parent is not None:
				if root.low_end <= root.parent.low_end:
					print ", is left child of interval node " + "[" + str(root.parent.low_end) \
					+ "-" + str(root.parent.high_end) + "]" + ' of value ' + str(root.parent.value)
				else:
					print ", is right child of interval node " + "[" + str(root.parent.low_end) \
					+ "-" + str(root.parent.high_end) + "]" + ' of value ' + str(root.parent.value)
			else:
				print ", is root node"
			self.printTreeString(root.left)
			self.printTreeString(root.right)
	
	#work to be done here------------------------------------Vasileios
	#XML format style:
	#<root>
	#	<low_end> % </low_end>
	#	<high_end> % </high_end>
	# <max_high> % </max_high>
	# <value> % </value>
	# <left_child> ...
	# </left_child>
	# <right_child> ...
	# </right_child>
	#</root>
	'''	
	def formXMLTree(self, root):
		if root is None:
			pass
		else:
			if root.parent is None:
				xmlroot = 
			else:
			
			self.formXMLTree(root.left)
			self.formXMLTree(root.right)
	'''
			
	def printOverlapList(self, ovList, ovIvalStart, ovIvalStop):
		print "Overlapping intervals with " + "[" + str(ovIvalStart) + "-" + str(ovIvalStop) + "] :"
		for i in ovList:
			print "[" + str(i.low_end) + "-" + str(i.high_end) + "]" 

	
	
	
