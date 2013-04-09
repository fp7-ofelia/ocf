from threading import Thread, Lock
from utils.Logger import Logger

'''
	@author: msune

	Ofelia XEN Agent Service Thread class 
'''

class ServiceThread(Thread):

	logger= Logger.getLogger()
	
	def __init__(self, serv_method, param, url):
		Thread.__init__(self)
		self.__method = serv_method	
		self.__param = param
		self.callback_url = url

	@staticmethod
	def start_method(service_method, param, url):
		thread=None
		ServiceThread(service_method, param, url).start()

	def run(self):	
		self.__method(self.__param)

