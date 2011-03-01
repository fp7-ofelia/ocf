import xmlrpclib

# Copied from the GENI test harness
class SafeTransportWithCert(xmlrpclib.SafeTransport):

    def __init__(self, use_datetime=0, keyfile=None, certfile=None):
        xmlrpclib.SafeTransport.__init__(self, use_datetime)
        self.__x509 = dict()
        if keyfile:
            self.__x509['key_file'] = keyfile
        if certfile:
            self.__x509['cert_file'] = certfile

    def make_connection(self, host):
        host_tuple = (host, self.__x509)
        return xmlrpclib.SafeTransport.make_connection(self, host_tuple)
    
class PrintingSafeTransportWithCert(xmlrpclib.SafeTransport):

    def __init__(self, use_datetime=0, keyfile=None, certfile=None):
        xmlrpclib.SafeTransport.__init__(self, use_datetime)
        self.__x509 = dict()
        if keyfile:
            self.__x509['key_file'] = keyfile
        if certfile:
            self.__x509['cert_file'] = certfile

    def make_connection(self, host):
        host_tuple = (host, self.__x509)
        return xmlrpclib.SafeTransport.make_connection(self, host_tuple)

    def _parse_response(self, file, sock):
        # read response from input file/socket, and parse it

        p, u = self.getparser()

        print "******Got response:\n"
        while 1:
            if sock:
                response = sock.recv(1024)
            else:
                response = file.read(1024)
            if not response:
                break
            if self.verbose:
                print "body:", repr(response)

            print "%s" % response
            p.feed(response)

        file.close()
        p.close()

        return u.close()
    