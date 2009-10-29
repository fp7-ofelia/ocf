import xmlrpclib

from ApiExceptionCodes import *

VerboseExceptions = False

def EnableVerboseExceptions(x=True):
    global VerboseExceptions
    VerboseExceptions = x

class ExceptionUnmarshaller(xmlrpclib.Unmarshaller):
    def close(self):
        try:
            return xmlrpclib.Unmarshaller.close(self)
        except xmlrpclib.Fault, e:
            # if the server tagged some traceback info onto the end of the
            # exception text, then print it out on the client.

            if "\nFAULT_TRACEBACK:" in e.faultString:
                parts = e.faultString.split("\nFAULT_TRACEBACK:")
                e.faultString = parts[0]
                if VerboseExceptions:
                    print "\n|Server Traceback:", "\n|".join(parts[1].split("\n"))

            raise e

class ExceptionReportingTransport(xmlrpclib.Transport):
    def make_connection(self, host):
        import httplib
        if host.startswith("https:"):
           return httplib.HTTPS(host)
        else:
           return httplib.HTTP(host)

    def getparser(self):
        unmarshaller = ExceptionUnmarshaller()
        parser = xmlrpclib.ExpatParser(unmarshaller)
        return parser, unmarshaller

class BaseClient():
    def __init__(self, url):
        self.url = url
        self.server = xmlrpclib.ServerProxy(self.url, ExceptionReportingTransport())

    def noop(self, value):
        return self.server.noop(value)
