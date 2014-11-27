from rspecs.src.geni.v3.container.resource import Resource

class Link(Resource):
    
    def __init__(self):
        Resource.__init__(self)
        self.__source_id = None
        self.__dest_id = None
        self.__type = None
        #TODO add fancy fields
        self.__capacity = None
        self.__latency = None
        

    def get_source_id(self):
        return self.__source_id


    def get_dest_id(self):
        return self.__dest_id


    def get_type(self):
        return self.__type


    def get_capacity(self):
        return self.__capacity


    def get_latency(self):
        return self.__latency


    def set_source_id(self, value):
        self.__source_id = value


    def set_dest_id(self, value):
        self.__dest_id = value


    def set_type(self, value):
        self.__type = value


    def set_capacity(self, value):
        self.__capacity = value


    def set_latency(self, value):
        self.__latency = value

        