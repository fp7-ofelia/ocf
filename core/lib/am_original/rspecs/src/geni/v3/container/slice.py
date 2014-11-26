class Slice:

    def __init__(self):
        self.__id = None
        self.__urn = None
        self.__expiration = None
        self.__operational_state = None
        self.__client_id = None
        self.__slivers = list()
    
    def get_client_id(self):
        return self.__client_id
    
    def set_client_id(self, value):
        self.__client_id = value
    
    def get_id(self):
        return self.__id
    
    def get_urn(self):
        return self.__urn
    
    def get_expiration(self):
        return self.__expiration
    
    def get_status(self):
        return self.__operational_state
    
    def get_slivers(self):
        return self.__slivers
    
    def set_id(self, value):
        self.__id = value
    
    def set_urn(self, value):
        self.__urn = value
    
    def set_expiration(self, value):
        self.__expiration = value
    
    def set_status(self, value):
        self.__operational_state = value
    
    def set_slivers(self, value):
        self.__slivers = value
    
    def __str__(self):
        to_return = self.__class__.__name__ + " [ "
        for attr in self.__dict__.keys():
            new_attr = attr + "=" + str(getattr(self, attr)) + ", "
            to_return += new_attr
        to_return += "]"
        return to_return
    
    def __repr__(self):
        return self.__str__()

