import time
import urllib2
import threading
import random

class ServiceThread(threading.Thread):

        __method = None
        __param = None
        callBackURL=None
        requestUser =None

        @staticmethod
        def startMethodInNewThread(servmethod,param, requestUser = None, url = None):
                thread = ServiceThread()
                thread.callBackURL = url
                thread.requestUser = requestUser
                thread.startMethod(servmethod,param)
        def startMethod(self,servmethod,param):
                self.__method = servmethod
                self.__param = param
                self.start()

        def run(self):
                self.__method(self.__param)



class Driver(threading.Thread):
    """
    Produces random integers to a list
    """
    _lockers  = dict()

    def __init__(self, integer, event):
        threading.Thread.__init__(self)
        self.integer = integer
        self.event = event
    
    def run(self):
	Driver._lockers[self.integer] = self.event
	print 'Lockers', self._lockers
	print 'waiting'
	self.event.wait()
	print 'Now I will continue, by the way i manage the locker %d' % self.integer

    @staticmethod
    def crudVM(integer):
	ServiceThread.startMethodInNewThread(Dispatcher.makeVM, integer)

    @staticmethod
    def ReleaseVM(integer):
	Driver._lockers[integer].set()
	del Driver._lockers[integer]
	

class Dispatcher(threading.Thread):

    def __init__(self, integer):
        threading.Thread.__init__(self)
        self.integers = integer

    @staticmethod
    def makeVM(integer):
	print 'I am managinc RSpec...'
	time.sleep(1)
	print 'I ve just sent the RSpec to the Agent'
	ServiceThread.startMethodInNewThread(ResponseDispatcher.responseDriver,integer)

class ResponseDispatcher(threading.Thread):

    @staticmethod
    def responseDriver(integer):
	print "the vm with id %d is ok" % integer
	ServiceThread.startMethodInNewThread(Driver.ReleaseVM,integer)

def test(i):
       event = threading.Event()
       dvr = Driver(i,event)
       dvr.start()
       dvr.crudVM(i)


def main():
    for i in range(3):
	ServiceThread.startMethodInNewThread(test,i)

if __name__ == '__main__':
    main()
 
