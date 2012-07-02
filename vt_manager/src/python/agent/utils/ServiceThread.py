from threading import Thread

'''
	@author: msune

	Ofelia XEN Agent Service Thread class 
'''


class ServiceThread(Thread):
	
	__method = None	
	__param = None
	callBackURL=None

	@staticmethod
	def startMethodInNewThread(servmethod,param,url):
		thread = ServiceThread()	
		thread.callBackURL = url
		thread.startMethod(servmethod,param)

	def startMethod(self,servmethod,param):
		self.__method = servmethod
		self.__param = param
		self.start()

	def run(self):	
		self.__method(self.__param)			
