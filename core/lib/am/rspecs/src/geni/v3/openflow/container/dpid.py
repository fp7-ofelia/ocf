from rspecs.src.geni.v3.container.resource import Resource

class DPID(Resource):
    
    def __init__(self):
        Resource.__init__(self)
        self.__datapath = None
        self.__ports = list()

    def get_datapath(self):
        return self.__datapath


    def get_ports(self):
        return self.__ports


    def set_datapath(self, value):
        self.__datapath = value


    def set_ports(self, value):
        self.__ports = value
        
    def add_port(self, value):
        if not self.__ports:
            self.__ports = list()
        self.__ports.append(value)

        
    