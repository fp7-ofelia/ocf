import sys
sys.path.append("/opt/ofelia/AMsoil/src/src/vendor/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/src/")
sys.path.append("/opt/ofelia/AMsoil/src/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)
from models.common.expiration import *
from models.resources.virtualmachine import *
exp = Expiration()
vm = VirtualMachine.query.first()
exp.do_save = True
exp.set_virtualmachine(vm)
