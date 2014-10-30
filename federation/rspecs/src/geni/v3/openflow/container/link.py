from rspecs.src.geni.v3.container.resource import Resource

class Link(Resource):
    
    def __init__(self):
        Resource.__init__(self)
        self.__src_dpid = None
        self.__src_port = None
        self.__dst_dpid = None
        self.__dst_port = None

    def get_src_dpid(self):
        return self.__src_dpid


    def get_src_port(self):
        return self.__src_port


    def get_dst_dpid(self):
        return self.__dst_dpid


    def get_dst_port(self):
        return self.__dst_port


    def set_src_dpid(self, value):
        self.__src_dpid = value


    def set_src_port(self, value):
        self.__src_port = value


    def set_dst_dpid(self, value):
        self.__dst_dpid = value


    def set_dst_port(self, value):
        self.__dst_port = value
