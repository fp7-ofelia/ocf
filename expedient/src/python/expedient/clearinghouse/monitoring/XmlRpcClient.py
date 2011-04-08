import xmlrpclib

'''
author:msune
Server monitoring thread
'''

class XmlRpcClient():

    '''
    Calling a remote method with variable number of parameters
    '''
    @staticmethod
    def callRPCMethod(url,methodName,*params):

        try:
            aggregate= xmlrpclib.Server(url)
            getattr(aggregate,methodName)(params)
        except Exception as e:
            print "XMLRPC Client error: "
            print e 
            raise e
