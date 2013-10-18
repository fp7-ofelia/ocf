#from foam.flowclashdetection.interval_structure import IValNode, IValTree
from interval_structure import IValNode, IValTree

if __name__ == '__main__':
	ivtree = IValTree()
	print "Test 1"
	ivtree.root = ivtree.addIVal(ivtree.root, 10, 20, "slice1")
	ivtree.root = ivtree.addIVal(ivtree.root, 30, 50, "slice2")
	ivtree.root = ivtree.addIVal(ivtree.root, 20, 60, "slice3")
	ivtree.root = ivtree.addIVal(ivtree.root, 10, 20, "slice4")
	ivtree.root = ivtree.addIVal(ivtree.root, 30, 50, "slice5")
	ivtree.root = ivtree.addIVal(ivtree.root, 20, 60, "slice6")
	ivtree.root = ivtree.addIVal(ivtree.root, 10, 20, "slice7")
	ivtree.root = ivtree.addIVal(ivtree.root, 30, 50, "slice8")
	ivtree.root = ivtree.addIVal(ivtree.root, 20, 60, "slice9")
	print "This is the tree:"
	ivtree.printTreeString(ivtree.root)
	print "Removal tests......................................."
	print "Test 2"
	ivtree.printOverlapList(ivtree.findOverlapIVal(ivtree.root, 30, 40, []), 30, 40)
	print "Test 3"
	ivtree.root = ivtree.remIVal(ivtree.root, 10, 20, "slice1")
	ivtree.printTreeString(ivtree.root)
	print "Test 4"
	ivtree.root = ivtree.remIVal(ivtree.root, 20, 60, "slice3")
	ivtree.printTreeString(ivtree.root)
	print "Test 5"
	ivtree.root = ivtree.remIVal(ivtree.root, 30, 50, "slice2")
	ivtree.printTreeString(ivtree.root)
	
