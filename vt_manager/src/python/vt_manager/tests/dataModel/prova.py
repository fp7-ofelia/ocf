import os
import sys
from os.path import dirname, join

PYTHON_DIR = join(dirname(__file__), '/opt/ofelia/vt_manager/src/python/')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'vt_manager.settings'

sys.path.insert(0,PYTHON_DIR)


from vt_manager.models.VTServer import VTServer
from vt_manager.models.XenServer import XenServer
from vt_manager.models.XenVM import XenVM
from vt_manager.models.Ip4Range import Ip4Range
from vt_manager.models.MacRange import MacRange

def createVTServer():
	
	server = XenServer.constructor("nom","GNU/Linux","Debian","6.0","")
	server.addDataBridge("peth2","00:11:22:33:44:55","984854",2)
	try: 
		server.addDataBridge("peth3","00:11:22:33:44:55","984854",2) 
	except Exception as e:
		print e
	#server.setMgmtBridge("peth3","00:11:22:33:44:T5") 
	server.setMgmtBridge("peth3","00:11:22:33:44:a5") 
	server.setMgmtBridge("peth4","00:11:22:33:44:a6") 
	return server	

macRange = MacRange.objects.get(name="nouRange2")
macRange.allocateMac()
sys.exit()
server = createVTServer()

#server = XenServer.objects.get(name="nom")

#vm = server.vms.get(name="novaVM")
#server.deleteVM(vm)

#sys.exit()
#server = VTServer.objects.get(id=55)
#server.createVM()
#sys.exit()

Ip4Range.constructor("nouRange2","192.168.0.0","192.168.0.255","255.255.255.0","192.168.0.1","195.235.113.3","")
ipRange = Ip4Range.objects.get(name="nouRange2")

#ipRange.addExcludedIp("192.168.0.1")
#ipRange.addExcludedIp("192.168.0.2")

macRange = MacRange.constructor("nouRange2","00:00:00:00:00:00","00:FF:FF:FF:FF:FF")

print "a"

import time
macRange.addExcludedMac("00:00:00:00:00:01")
time.sleep(20)
macRange.addExcludedMac("00:00:00:00:00:02")
time.sleep(20)
macRange.addExcludedMac("00:00:00:00:00:03")
sys.exit()
#macRange.addExcludedMac("00:00:00:00:00:02")

#i=0
#while True:
#	i+=1
#	if i == 100:
#		break
#	mac = macRange.allocateMac().getMac()
#	print mac


#	def createVM(self,name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,hdSetupType,hdOriginPath,virtSetupType,save=True):
server = XenServer.objects.get(name="nom")

server.createVM("novaVM","uuid2","projectId","projectName","sliceId","sliceName","GNU/Linux","6.0","Debian",512,1000,4,"","file-image","originPath","xen")


time.sleep(20)

server = XenServer.objects.get(id=1)
#server.createVM()
vm = server.vms.get(name="novaVM")
server.deleteVM(vm)


sys.exit()

i=0
while True:
	print "c"
	import time
	#time.sleep(1)
	ip = ipRange.allocateIp().getIp()
	print ip
