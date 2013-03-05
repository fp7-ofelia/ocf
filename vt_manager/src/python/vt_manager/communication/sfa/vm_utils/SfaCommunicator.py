import threading
from vt_manager.utils.ServiceThread import ServiceThread
from vt_manager.controller.dispatchers.xmlrpc.ProvisioningDispatcher import ProvisioningDispatcher



class SfaCommunicator(threading.Thread):

    _SFALockers  = dict()
    SFAUrl = 'SFA.OCF.VTM'

    def __init__(self, actionID,event,rspec):
        threading.Thread.__init__(self)
	self.actionID = actionID
	self.event = event
	self.rspec = rspec

    def run(self):
        SfaCommunicator._SFALockers[self.actionID] = self.event
	self.DispatchProvisioningAction()
        #self.event.wait()
	#TODO: Do something here
	return

    def DispatchProvisioningAction(self):
	try:
	    ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,self.rspec, self.SFAUrl)
	    self.__lock()
	except Exception as e:
	    SfaCommunicator.__release(self.actionID)
	    raise e

    def __lock(self):
	self.event.wait()
	SfaCommunicator._SFALockers[self.actionID] = self.event

    @staticmethod
    def __release(actionID):
	try:
	    SfaCommunicator._SFALockers[actionID].set()
	    del SfaCommunicator._SFALockers[actionID]
	except Exception as e:
	    print 'SFALockers:',SfaCommunicator._SFALockers
	    raise e

    @staticmethod
    def ResponseActionRecieved(actionID,actionStatus):
        SfaCommunicator.__release(actionID)
	#XXX: could we get the true action status?
	return
	#TODO: do something if necessary

