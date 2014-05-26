import xmlrpclib

"""
author: msune, CarolinaFernandez
Server monitoring thread
"""

class XmlRpcClient(object):

    @staticmethod
    def call_method(url, method_name, *params):
        """
        Calling a remote method with variable number of parameters.
        """
        try:
            aggregate = xmlrpclib.Server(url)
            return getattr(aggregate, method_name)(params)
        except Exception as e:
            print "XMLRPC Client error: %s" % str(e)
            raise e
