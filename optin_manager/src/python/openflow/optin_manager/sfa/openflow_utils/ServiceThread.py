from threading import Thread

class ServiceThread(Thread):
	
	__method = None	
	__params = None
	callBackURL=None
	event = None

	@staticmethod
	def startMethodInNewThread(servmethod, params, url=None):
		thread = ServiceThread()	
		thread.callBackURL = url
                if not isinstance(params,list):
                	params = [params]
		thread.startMethod(servmethod,params)
	def startMethod(self,servmethod,params):
		self.__method = servmethod
		self.__params = params
		self.start()

	def run(self):	
		self.__method(*self.__params)			
