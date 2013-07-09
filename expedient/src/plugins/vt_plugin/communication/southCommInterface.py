from vt_manager.communication.utils.XmlHelper import *
from vt_plugin.utils.ServiceThread import *
from expedient.common.rpc4django import rpcmethod
from vt_plugin.controller.dispatchers.ProvisioningResponseDispatcher import ProvisioningResponseDispatcher
from vt_plugin.controller.dispatchers.MonitoringResponseDispatcher import MonitoringResponseDispatcher

@rpcmethod(signature=['string'], url_name = 'vt_am')
def sendAsync(xml):
    
    """method that will be used by the VT AM to send inputs to the VT Plugin"""
    
    rspec = XmlHelper.parseXmlString(xml)
    if rspec.response.monitoring:
        ServiceThread.startMethodInNewThread(MonitoringResponseDispatcher.processResponse ,rspec.response.monitoring)
    if rspec.response.provisioning:
	ServiceThread.startMethodInNewThread(ProvisioningResponseDispatcher.processResponse ,rspec.response.provisioning)
    return ""


