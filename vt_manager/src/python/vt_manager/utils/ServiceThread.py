from threading import Thread

class ServiceThread(Thread):
	
	__method = None	
	__param = None
	callBackURL=None
	event = None

	@staticmethod
	def startMethodInNewThread(servmethod,param,url = None):
		thread = ServiceThread()	
		thread.callBackURL = url
		thread.startMethod(servmethod,param)
	def startMethod(self,servmethod,param):
		self.__method = servmethod
		self.__param = param
		self.start()

	def run(self):	
		self.__method(self.__param)			
