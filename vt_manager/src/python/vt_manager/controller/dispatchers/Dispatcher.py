from vt_manager.communication.utils.XmlUtils import XmlHelper
from vt_manager.models import *
from vt_manager.controller.policy.PolicyManager import PolicyManager
import xmlrpclib, threading, logging, copy
from vt_manager.settings import ROOT_USERNAME, ROOT_PASSWORD, VTAM_URL
from vt_manager.communication.XmlRpcClient import XmlRpcClient
CONTROLLER_TYPE_XEN = "xen"


class Dispatcher():

	@staticmethod
	def prefijo__connectAndSendAgent(Server, action):
		if not Server.getAvailable():
			raise Exception("Server is not available at the moment")

		XmlRpcClient.callRPCMethod(Server.getAgentURL() ,"send", "https://"+ROOT_USERNAME+":"+ROOT_PASSWORD+"@"+VTAM_URL, 1, "hfw9023jf0sdjr0fgrbjk",XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action)) )

	@staticmethod
	def prefijo__connectAndSendPlugin(url, rspec):
		XmlRpcClient.callRPCMethod(url,"sendAsync",rspec)

