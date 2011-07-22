import xmlrpclib
from urlparse import urlparse
'''
author:msune
Server monitoring thread
'''

class XmlRpcClient():

	'''
	Calling a remote method with variable number of parameters
	'''

	@staticmethod
	def callRPCMethodBasicAuth(url,userName,password,methodName,*params):
		#Incrust basic authentication
		parsed = urlparse(url)
		newUrl = parsed.scheme+"://"+userName+":"+password+"@"+parsed.netloc+parsed.path
		if not parsed.query == "":
			newUrl += "?"+parsed.query
		XmlRpcClient.callRPCMethod(newUrl,methodName,*params)	
	@staticmethod
	def callRPCMethod(url,methodName,*params):
		try:
			server = xmlrpclib.Server(url)
			getattr(server,methodName)(*params)
		except Exception as e:
			print "XMLRPC Client error: can't connect to method %s at %s" % (methodName, url)
			print e 
			raise e
