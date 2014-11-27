from rspecs.src.geni.v3.container.resource import Resource

class Match(Resource):
    
    def __init__(self):
        Resource.__init__(self)
        self.__group = None
        self.__dl_src = list()
        self.__dl_dst = list()
        self.__dl_type = list()
        self.__dl_vlan = list()
        self.__nw_src = list()
        self.__nw_dst = list()
        self.__nw_proto = list()
        self.__tp_src = list()
        self.__tp_dst = list()

    def get_group(self):
        return self.__group

    def get_dl_src(self):
        return self.__dl_src


    def get_dl_dst(self):
        return self.__dl_dst


    def get_dl_type(self):
        return self.__dl_type


    def get_dl_vlan(self):
        return self.__dl_vlan


    def get_nw_src(self):
        return self.__nw_src


    def get_nw_dst(self):
        return self.__nw_dst


    def get_nw_proto(self):
        return self.__nw_proto


    def get_tp_src(self):
        return self.__tp_src


    def get_tp_dst(self):
        return self.__tp_dst
    
    
    def set_group(self, value):
        self.__group = value
        
        
    def set_dl_src(self, value):
        self.__dl_src = value


    def set_dl_dst(self, value):
        self.__dl_dst = value


    def set_dl_type(self, value):
        self.__dl_type = value


    def set_dl_vlan(self, value):
        self.__dl_vlan = value


    def set_nw_src(self, value):
        self.__nw_src = value


    def set_nw_dst(self, value):
        self.__nw_dst = value


    def set_nw_proto(self, value):
        self.__nw_proto = value


    def set_tp_src(self, value):
        self.__tp_src = value


    def set_tp_dst(self, value):
        self.__tp_dst = value

    def add_dl_src(self, value):
        self.__dl_src.append(value)


    def add_dl_dst(self, value):
        self.__dl_dst.append(value)


    def add_dl_type(self, value):
        self.__dl_type.append(value)


    def add_dl_vlan(self, value):
        self.__dl_vlan.append(value)


    def add_nw_src(self, value):
        self.__nw_src.append(value)


    def add_nw_dst(self, value):
        self.__nw_dst.append(value)


    def add_nw_proto(self, value):
        self.__nw_proto.append(value)


    def add_tp_src(self, value):
        self.__tp_src.append(value)


    def add_tp_dst(self, value):
        self.__tp_dst.append(value)    
        
        
        
        
        