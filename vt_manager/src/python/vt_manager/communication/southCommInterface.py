from django.http import *
import os, sys, logging
from vt_manager.models import *
from vt_manager.controller import *
from vt_manager.communication.utils.XmlHelper import *
from vt_manager.utils.ServiceThread import *
from vt_manager.common.rpc4django import rpcmethod
from vt_manager.common.rpc4django import *
from vt_manager.controller.dispatchers.xmlrpc.DispatcherLauncher import DispatcherLauncher
from vt_manager.utils.SyncThread import *


@rpcmethod(url_name="agent", signature=['string', 'string'])
def sendAsync(xml):
	logging.debug("sendAsync lauched")
	rspec = XmlHelper.parseXmlString(xml)
	ServiceThread.startMethodInNewThread(DispatcherLauncher.processXmlResponse ,rspec)
	#ServiceThread.startMethodInNewThread(ProvisioningResponseDispatcher.processResponse , rspec)
	return

@rpcmethod(ulr_name="agent", signature=['string', 'string'])
def sendSync(xml):
	logging.debug("sendSync lauched")
	rspec = XmlHelper.parseXmlString(xml)
	SyncThread.startMethodAndJoin(DispatcherLauncher.processXmlResponseSync, rspec)
	return

