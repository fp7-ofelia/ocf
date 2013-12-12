import sys
sys.path.append('/opt/ofelia/AMsoil/src')
sys.path.append('/opt/ofelia/AMsoil/vtamrm')

from utils.commonbase import db_session
from resources.xenserver import VTServer
from controller.drivers.virt import VTDriver

#print VTServer.__subclass__()

server = db_session.query(VTServer).first()

print server.name

xenserver = server.getChildObject()

print xenserver

servers = VTDriver.getAllServers()

print servers
