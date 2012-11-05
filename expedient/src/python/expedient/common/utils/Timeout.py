import xmlrpclib
import httplib
from expedient.common.utils.transport import TestClientTransport
# Generates a circular dependency --> remove!
#from expedient.common.xmlrpc_serverproxy.models import BasicAuthServerProxy

'''
        @author: CarolinaFernandez
        @see: http://stackoverflow.com/questions/372365/set-timeout-for-xmlrpclib-serverproxy#2116786

        Add timeout property to xmlrpclib.Server
'''

class TimeoutHTTPConnection(httplib.HTTPConnection):
   def connect(self):
       httplib.HTTPConnection.connect(self)
       self.sock.settimeout(self.timeout)

class TimeoutHTTP(httplib.HTTP):
   _connection_class = TimeoutHTTPConnection
   def set_timeout(self, timeout):
       self._conn.timeout = timeout

#class TimeoutTransport(xmlrpclib.Transport):
class TimeoutTransport(TestClientTransport):
    def __init__(self, timeout=10, *l, **kw):
        print "**************** init TimeoutTransport"
#        xmlrpclib.Transport.__init__(self,*l,**kw)
        TestClientTransport.__init__(self,*l,**kw)
        self.timeout=timeout
    def make_connection(self, host):
        print "**************** make_connection TimeoutTransport"
        conn = TimeoutHTTP(host)
        conn.set_timeout(self.timeout)
        return conn

class TimeoutServerProxy(BasicAuthServerProxy):
    def __init__(self,uri,timeout=10,*l,**kw):
        kw['transport']=TimeoutTransport(timeout=timeout, use_datetime=kw.get('use_datetime',0))
        xmlrpclib.ServerProxy.__init__(self,uri,*l,**kw)
