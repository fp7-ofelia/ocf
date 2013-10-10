import xmlrpclib
from vt_manager.communication.northCommInterface import send_sync
from uuid import uuid4
from vt_manager.communication.utils.XmlHelper import *

rspec = open("/opt/ofelia/vt_manager/src/python/vt_manager/tests/provisioning/pruebaCreate.xml").read()
url = "https://xml:rpc@10.216.12.5:8445/xmlrpc/plugin"
callBackUrl = "https://llull.ctx.i2cat.net:38445/xmlrpc/plugin"

rspec = XmlHelper.parseXmlString(rspec)
rspec.query.provisioning.action[0].id = "fakeID:" + str(uuid4())
rspec.query.provisioning.action[0].server.virtual_machines[0].uuid = "fakeID:" + str(uuid4())
rspec.query.provisioning.action[0].server.virtual_machines[0].name = "fakeVM" + str(uuid4())[0:3]
rspec = XmlHelper.craftXmlClass(rspec)

s = xmlrpclib.Server(url, verbose=True)
print s.send_sync("", rspec)
