<<<<<<< HEAD
import xmlrpclib
=======
import xmlrpclib, logging
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
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
<<<<<<< HEAD
		XmlRpcClient.callRPCMethod(newUrl,methodName,*params)	
=======
		try:
			XmlRpcClient.callRPCMethod(newUrl,methodName,*params)	
		except Exception:
                        raise 

>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
	@staticmethod
	def callRPCMethod(url,methodName,*params):
		try:
			server = xmlrpclib.Server(url)
			getattr(server,methodName)(*params)
		except Exception as e:
<<<<<<< HEAD
			print "XMLRPC Client error: can't connect to method %s at %s" % (methodName, url)
			print e 
=======
                        turl=url.split('@')
			if len(turl)>1:
				url = turl[0].split('//')[0]+'//'+turl[-1]
			te =str(e)
			if '@' in te:
				e=te[0:te.find('for ')]+te[te.find('@')+1:]	
			logging.error("XMLRPC Client error: can't connect to method %s at %s" % (methodName, url))
			logging.error(e)
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
			raise Exception("XMLRPC Client error: can't connect to method %s at %s\n" % (methodName, url) + str(e))
