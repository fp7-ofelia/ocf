from django.http import *
import logging
from vt_manager.models import *
from vt_manager.controller import *
from vt_manager.communication.utils.XmlHelper import *
from vt_manager.utils.ServiceThread import *
from vt_manager.common.rpc4django import rpcmethod
from vt_manager.common.rpc4django import *
from vt_manager.controller.dispatchers.launcher import DispatcherLauncher

@rpcmethod(url_name="agent", signature=['string', 'string'])
def sendAsync(xml):
	logging.debug("sendAsync launched")
	rspec = XmlHelper.parseXmlString(xml)
	logging.debug("RSPEC")
	logging.debug("------------------------------------------------")
	logging.debug(xml)
	logging.debug("------------------------------------------------")
	ServiceThread.startMethodInNewThread(DispatcherLauncher.process_response, rspec)
	#ServiceThread.startMethodInNewThread(ProvisioningResponseDispatcher.process, rspec)
	return
