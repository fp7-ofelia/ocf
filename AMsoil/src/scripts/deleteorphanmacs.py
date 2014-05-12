import sys
sys.path.append("/opt/ofelia/AMsoil/src/src/vendor/configdb/")
sys.path.append("/opt/ofelia/AMsoil/src/src/")
sys.path.append("/opt/ofelia/AMsoil/src/src/vendor/virtrm")
import amconfigdb
import amconfigdbexceptions
import amsoil.core.pluginmanager as pm
pm.registerService("config", amconfigdb.ConfigDB())
pm.registerService("configexceptions", amconfigdbexceptions)
from models.interfaces.networkinterface import NetworkInterface
from models.resources.macslot import MacSlot
from models.ranges.macrange import MacRange
from models.resources.ip4slot import Ip4Slot
from models.ranges.ip4range import Ip4Range

macs = MacSlot.query.all()

for mac in macs:
    if not mac.networkInterface:
        mac.destroy()
