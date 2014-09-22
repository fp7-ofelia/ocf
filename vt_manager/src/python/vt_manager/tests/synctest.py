from uuid import uuid4
from vt_manager.communication.northCommInterface import send_sync
from vt_manager.communication.utils.XmlHelper import *
import os

rspec = open(os.path.join(os.path.dirname(__file__), "provisioning/pruebaCreate.xml")).read()
url = "https://xml:rpc@llull.ctx.i2cat.net:38445/xmlrpc/plugin"

rspec = XmlHelper.parseXmlString(rspec)
rspec.query.provisioning.action[0].id = "fakeID:" + str(uuid4())
rspec.query.provisioning.action[0].server.virtual_machines[0].uuid = "fakeID:" + str(uuid4())
rspec.query.provisioning.action[0].server.virtual_machines[0].name = "fakeVM" + str(uuid4())[0:3]
rspec = XmlHelper.craftXmlClass(rspec)

send_sync(url, rspec)
