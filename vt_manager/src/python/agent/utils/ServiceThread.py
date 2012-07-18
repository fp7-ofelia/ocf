from threading import Thread
from utils.Logger import Logger

'''
	@author: msune

	Ofelia XEN Agent Service Thread class 
'''


class ServiceThread(Thread):
	
	__method = None	
	__param = None
	callBackURL=None
	actionId = None

	logger= Logger.getLogger()

	@staticmethod
	def startMethodInNewThread(servmethod,param,url, actionId):
		thread = ServiceThread()	
		thread.callBackURL = url
		thread.startMethod(servmethod,param)
		thread.actionId = actionId

	def startMethod(self,servmethod,param):
		self.__method = servmethod
		self.__param = param
		self.start()

	def run(self):	
		self.__method(self.__param)
		self.logger.debug("Terminating service thread execution: "+self.actionId)
