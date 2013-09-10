import threading
from vt_manager.utils.ServiceThread import ServiceThread
from vt_manager.controller.dispatchers.xmlrpc.ProvisioningDispatcher import ProvisioningDispatcher
from vt_manager.common.middleware.thread_local import thread_locals, push
import multiprocessing


class SfaCommunicator(multiprocessing.Process):

    _SFALockers  = dict()
    SFAUrl = 'SFA.OCF.VTM'
    callBackURL = None
    

    def __init__(self, actionID,event,rspec):
        multiprocessing.Process.__init__(self)
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
	ST = ServiceThread()
	ST.callBackURL = self.SFAUrl
	#ST.event = self.event
	print 'thread_locals',thread_locals.stack
	push('12345',self.event)
	push(str(self.actionID),self.event)
	print thread_locals.stack
        ST.startMethod(ProvisioningDispatcher.processProvisioning,self.rspec)
	ST.join()
        print 'end of dispatching'
        return
	

