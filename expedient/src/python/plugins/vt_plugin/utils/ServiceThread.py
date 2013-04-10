from threading import Thread

class ServiceThread(Thread):

        # TODO: import from expedient.common.utils.ServiceThread,
        # adapt arguments being passed (these will be a tuple now)
        # and remove this class.
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
