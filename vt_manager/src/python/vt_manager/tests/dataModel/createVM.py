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

server = XenServer.objects.get(name="nom")

server.createVM("novaVM","uuid2","projectId","projectName","sliceId","sliceName","GNU/Linux","6.0","Debian",512,1000,4,"","file-image","originPath","xen")

import time

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
