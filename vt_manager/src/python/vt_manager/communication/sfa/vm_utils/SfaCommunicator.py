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
	print 'setting lockers'
        SfaCommunicator._SFALockers[self.actionID] = self.event
	print 'dispatching Action'
	self.DispatchProvisioningAction()
        #self.event.wait()
	#TODO: Do something here
	return

    def DispatchProvisioningAction(self):
#	try:
        print 'dispatching Action'
        print self.SFAUrl
        #ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,self.rspec, self.SFAUrl)
        self.callBackURL = self.SFAUrl
        self.event.set()
        ProvisioningDispatcher.processProvisioning(self.rspec)
        print 'end of dispatching'
	    #self.__lock()
#	except Exception as e:
#	    SfaCommunicator.__release(self.actionID)
#	    raise e

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

