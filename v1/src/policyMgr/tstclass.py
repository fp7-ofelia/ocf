import pm
A = pm.FlowSpace('0',1,'00:16:d3:ca:a0:f8','*','*','*','172.168.103.1/24', '172.168.102.3','4','80','*','12')
B = pm.FlowSpace('1',1,'*','*','*','*','172.168.204.1/24', '172.168.102.4','4','80','*','12')
C = pm.FlowSpace('2',1,'*','*','*','*','172.168.102.2/24', '172.168.102.3/24','4','80','*','12')
D = pm.FlowSpace('3',1,'*','*','*','*','172.168.103.2/16', '172.168.102.3/16','4','80','*','12')
E = pm.FlowSpace('',1,'*','*','*','*','172.162.102.2/24', '172.163.102.1/24','4','80','*','12')
F = pm.FlowSpace('',1,'00:00:00:00:00:00','00:00:00:00:00:00','0','0','0.0.0.0', '0.0.0.0','0','0','0','12')
G = pm.FlowSpace('',1,'00:00:00:00:00:00','00:00:00:00:00:00','0','0','0.0.255.0', '0.0.255.0','0','0','0','12')
H = pm.FlowSpace('',1,'00:00:00:00:00:00','00:00:00:00:00:00','65535','4095','255.255.255.255', '255.255.255.255','255','65535','65535','12')
I = pm.FlowSpace('',1,'00:00:00:00:00:00','00:00:00:00:00:00','0','0','0.255.255.255', '255.255.255.255','0','0','0','12')
#QFS = pm.bits2FlowSpace(Q)
#print pm.FlowSpace2bits(E)
#print pm.FlowSpace2bits(F)
#print pm.FlowSpace2bits(G)
#print pm.FlowSpace2bits(H)
print "case 1: No D bits. some /24 were reserved and request /16"
print "reservations: "
A.display()
B.display()
print "new request: "
D.display()
print "D bits     : " 
F.display()
print "result: "
pm.q_intersectionD([A,B],D,F)

print "========================\ncase 2: no D bits. /16 was reserved already"
print "reservations:"
A.display()
D.display()
print "new request: "
C.display()
print "D bits     : "
F.display()
print "result:"
pm.q_intersectionD([A,D],C,F)

#s1 = pm.FlowSpace2bits(E)
#s2 = pm.FlowSpace2bits(D)
#db = pm.FlowSpace2bits(F)
#print pm._is_or_positive(s1, s2, db)
#pm.which_q_intersect([A,B,C,D],E)

print "=======================\ncase 3: with D bits and other options available"
print "reservations:"
A.display()
C.display()
print "new request : "
B.display()
print "D bits      : "
G.display()
print "result:"
pm.q_intersectionD([A,C],B, G)

