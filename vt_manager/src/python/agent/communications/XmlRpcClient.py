import xmlrpclib
import threading
from utils.xml.vtRspecInterface import rspec
from utils.XmlUtils import *

class XmlRpcClient:

	@staticmethod
	def __craftResponseXml(actionId,status,description):
	
		rspec = XmlUtils.getEmptyResponseObject()
		
		rspec.response.provisioning.action[0].id = actionId
		rspec.response.provisioning.action[0].status = status
		rspec.response.provisioning.action[0].description = description
		return XmlCrafter.craftXML(rspec) 

	@staticmethod
	def sendAsyncProvisioningActionStatus(actionId,status,description):
		server = xmlrpclib.Server(threading.current_thread().callBackURL)
		print XmlRpcClient.__craftResponseXml(actionId,status,description)
		server.sendAsync(XmlRpcClient.__craftResponseXml(actionId,status,description))




