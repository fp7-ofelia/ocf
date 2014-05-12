from threading import Thread, Lock
from utils.Logger import Logger

'''
	@author: msune

	Ofelia XEN Agent Service Thread class 
'''

class ServiceThread(Thread):

	logger= Logger.getLogger()
	
	def __init__(self,servMethod, param, url):
		Thread.__init__(self)
		self.__method = servMethod	
		self.__param = param
		self.callBackURL=url

	@staticmethod
	def startMethodInNewThread(serviceMethod, param,url):
		thread=None
		ServiceThread(serviceMethod, param, url).start()

	def run(self):	
		self.logger.debug("Starting service thread")
		self.__method(self.__param)
		self.logger.debug("Terminating service thread")
