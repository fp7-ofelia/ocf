import threading
from vt_manager.utils.ServiceThread import ServiceThread

class SfaCommunicator(threading.Thread):

    _SFALockers  = dict()
    SFAUrl = 'SFA.OCF.VTM'

    def __init__(self, actionID,event):
        threading.Thread.__init__(self)
	self.actionID = actionID
	self.event = event

    def run(self,provisioningRSpec):
        SfaCommunicator._lockers[self.actionID] = self.event
	self.DispatchProvisioningAction(self,provisioningRSpec)
        #self.event.wait()
	#TODO: Do something here
	return

    def DispatchProvisioningAction(self,provisioningRSpec):
	try:
	    ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,provisioningRSpec, self.SFAUrl)
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

