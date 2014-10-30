from rspecs.src.geni.v3.container.resource import Resource

class Controller(Resource):
    
    def __init__(self):
        Resource.__init__(self)
        self.__uri = None
        self.__port = None
        self.__type = None
        self.__protocol = None

    def get_uri(self):
        return self.__uri


    def get_port(self):
        return self.__port


    def get_type(self):
        return self.__type

    def get_protocol(self):
        return self.__protocol

    def set_uri(self, value):
        self.__uri = value


    def set_port(self, value):
        self.__port = value


    def set_type(self, value):
        self.__type = value
        
    def set_protocol(self, value):
        self.__protocol = value

    def get_url(self):
        return "%s:%s:%d" % (self.__protocol, self.__uri, self.__port)
    
    def parse_url(self, url):
        parts = url.split(":")
        self.__protocol = parts[0]
        self.__uri = parts[1]
        self.__port = int(parts[2])
        
    
    
    