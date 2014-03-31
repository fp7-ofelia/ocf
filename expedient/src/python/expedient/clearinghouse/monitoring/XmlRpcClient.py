import xmlrpclib

"""
author:msune, CarolinaFernandez
Server monitoring thread
"""

class XmlRpcClient():

    """
    Calling a remote method with variable number of parameters
    """
    @staticmethod
    def callRPCMethod(url,methodName,*params):
        result = None
        try:
            aggregate = xmlrpclib.Server(url)
            result = getattr(aggregate,methodName)(params)
        except Exception as e:
            print "XMLRPC Client error: "
            print e 
            raise e
        return result
