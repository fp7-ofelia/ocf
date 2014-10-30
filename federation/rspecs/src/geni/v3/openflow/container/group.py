from rspecs.src.geni.v3.container.resource import Resource

class Group(Resource):
    
    def __init__(self):
        Resource.__init__(self)
        self.__name = None
        self.__dpids = list()
        self.__matches = list()

    def get_name(self):
        return self.__name


    def get_dpids(self):
        return self.__dpids


    def get_matches(self):
        return self.__matches


    def set_name(self, value):
        self.__name = value


    def set_dpids(self, value):
        self.__dpids = value


    def set_matches(self, value):
        self.__matches = value
        
                
    def add_dpid(self, value):
        self.__dpids.append(value)


    def add_match(self, value):
        self.__matches.append(value)
        
        
        
        