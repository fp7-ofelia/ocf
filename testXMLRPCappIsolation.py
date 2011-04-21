import xmlrpclib
import sys 


if not sys.argv[1]:
    print "Indicate number of tries"
    exit
print "XMLRPC APP ISOLATION TEST"
s = xmlrpclib.Server('https://house:house@192.168.254.193:8443/xmlrpc/xmlrpc/')

for i in range(int(sys.argv[1])):
    try:
        print "Attempt "+ str(i)
        s.system.listMethods()
    except Exception as e:
        print e
        break
