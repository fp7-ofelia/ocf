import logging
from controller import *
from utils.xmlhelper import *
from utils.servicethread import *
from controller.dispatchers.launcher import DispatcherLauncher

def sendAsync(xml):
	logging.debug("sendAsync launched")
	rspec = XmlHelper.parse_xml_string(xml)
	logging.debug("RSPEC")
	logging.debug("------------------------------------------------")
	logging.debug(xml)
	logging.debug("------------------------------------------------")
	ServiceThread.start_method_in_new_thread(DispatcherLauncher.process_response, rspec)
	return
