import xmlrpclib, logging
from urlparse import urlparse

"""
author: msune, CarolinaFernandez
Server monitoring thread
"""

class XmlRpcClient():

	"""
	Calling a remote method with variable number of parameters
	"""
	@staticmethod
	def callRPCMethodBasicAuth(url,userName,password,methodName,*params):
		result = None
		#Incrust basic authentication
		parsed = urlparse(url)
		newUrl = parsed.scheme+"://"+userName+":"+password+"@"+parsed.netloc+parsed.path
		if not parsed.query == "":
			newUrl += "?"+parsed.query
		try:
			result = XmlRpcClient.callRPCMethod(newUrl,methodName,*params)	
		except Exception:
                        raise
		return result

	@staticmethod
	def callRPCMethod(url,methodName,*params):
		result = None
		try:
			server = xmlrpclib.Server(url)
			result = getattr(server,methodName)(*params)
		except Exception as e:
                        turl=url.split('@')
			if len(turl)>1:
				url = turl[0].split('//')[0]+'//'+turl[-1]
			te =str(e)
			if '@' in te:
				e=te[0:te.find('for ')]+te[te.find('@')+1:]	
			logging.error("XMLRPC Client error: can't connect to method %s at %s" % (methodName, url))
			logging.error(e)
			raise Exception("XMLRPC Client error: can't connect to method %s at %s\n" % (methodName, url) + str(e))
		return result

