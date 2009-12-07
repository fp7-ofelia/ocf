import traceback
import xmlrpclib

FAULTCODE = 900

class UnhandledServerException(xmlrpclib.Fault):
    def __init__(self, type, value, tb):
        exc_str = ''.join(traceback.format_exception(type, value, tb))
        faultString = exc_str # "Unhandled exception: " + str(type) + "\n" + exc_str
        xmlrpclib.Fault.__init__(self, FAULTCODE + 1, faultString)

class BadRequestHash(xmlrpclib.Fault):    
   def __init__(self, hash = None):
        faultString = "bad request hash: " + str(hash)
        xmlrpclib.Fault.__init__(self, FAULTCODE + 2, faultString)
