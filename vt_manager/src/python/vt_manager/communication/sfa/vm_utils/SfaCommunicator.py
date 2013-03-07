import threading
from vt_manager.utils.ServiceThread import ServiceThread
from vt_manager.controller.dispatchers.xmlrpc.ProvisioningDispatcher import ProvisioningDispatcher



class SfaCommunicator(threading.Thread):

    _SFALockers  = dict()
    SFAUrl = 'SFA.OCF.VTM'
    callBackURL = None
    

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
        print 'dispatching Action'
        print self.SFAUrl
        self.callBackURL = self.SFAUrl
        ProvisioningDispatcher.processProvisioning(self.rspec)
        print 'end of dispatching'
	

    @staticmethod
    def __lock(actionID):
	try:
	    print SfaCommunicator._SFALockers
	    SfaCommunicator._SFALockers[actionID].wait()
	except Exception as e:
	    print 'SFALockers:',SfaCommunicator._SFALockers
            raise e

    @staticmethod
    def __release(actionID):
	try:
	    SfaCommunicator._SFALockers[actionID].set()
	    del SfaCommunicator._SFALockers[actionID]
	except Exception as e:
	    print 'SFALockers:',SfaCommunicator._SFALockers
	    raise e

    @staticmethod
    def ActionRecieved(actionID):
	SfaCommunicator.__lock(actionID)
	return

    @staticmethod
    def ResponseActionRecieved(actionID,actionStatus):
        SfaCommunicator.__release(actionID)
	#XXX: could we get the true action status?
	return
	#TODO: do something if necessary

