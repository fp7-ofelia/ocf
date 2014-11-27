from rspecs.src.geni.v3.container.resource import Resource

class Port(Resource):
    
    def __init__(self):
        Resource.__init__(self)
        self.__name = None
        self.__num = None
        self.__features = None

    def get_name(self):
        return self.__name

    def get_num(self):
        return self.__num

    def get_features(self):
        return self.__features

    def set_name(self, value):
        self.__name = value

    def set_num(self, value):
        self.__num = value

    def set_features(self, value):
        self.__features = value

        
        