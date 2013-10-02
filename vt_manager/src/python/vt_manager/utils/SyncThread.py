from threading import Thread

class SyncThread(Thread):

    __method = None
    __param = None
    event = None
    callBackURL = None

    @staticmethod
    def startMethodAndJoin(servmethod, param, url=None): 
	thread = SyncThread()
	thread.callBackUrl = url
        thread.startMethod(servmethod,param)
	thread.join()

    def startMethod(self,servmethod,param):
    	self.__method = servmethod
        self.__param = param
        self.start()

    def run(self):
        self.__method(self.__param)

