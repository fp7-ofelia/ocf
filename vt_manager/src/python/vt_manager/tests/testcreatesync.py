from vt_manager.models import *
import os
import xmlrpclib

am = xmlrpclib.Server("https://expedient:expedient@192.168.254.193:8445/xmlrpc/plugin")
#xml = open("/opt/ofelia/vt_manager/src/python/vt_manager/tests/xmltest.xml", "r").read()
xml = open(os.path.join(os.path.dirname(__file__), "xmltest.xml"), "r").read()

am.send_sync("https://expedient:expedient@llull.ctx.i2cat.net:38445/xmlrpc/plugin/",xml)
