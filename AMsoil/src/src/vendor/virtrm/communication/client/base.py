from abc import ABCMeta, abstractmethod

class Client():
	"""
	Calls remote methods with a number of parameters.
	To be implemented by different kind of clients. 
	"""
	
	__metaclass__ = ABCMeta
	
	@abstractmethod
	def call_method_basic_auth(url, user_name, password, method_name, *params):
		raise NotImplementedError()
	
	@abstractmethod
	def call_method(url, method_name, *params):
		raise NotImplementedError()
