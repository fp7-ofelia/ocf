class Resource:
    
    def __init__(self):
        self.__id = None # Name of the resource 
        self.__exclusive = None
        self.__urn = None
        self.__uuid = None
        self.__available = None
        self.__status = None
        self.__services = dict()
    
    def get_available(self):
        return self.__available
    
    def set_available(self, value):
        self.__available = value
    
    def get_id(self):
        return self.__id
    
    def get_services(self):
        return self.__services
    
    def set_services(self, services):
        self.__services = services
    
    def get_exclusive(self):
        return self.__exclusive
    
    def get_urn(self):
        return self.__urn
    
    def get_uuid(self):
        return self.__uuid
    
    def get_status(self):
        return self.__status
    
    def set_id(self, ID):
        self.__id = ID
    
    def set_exclusive(self, exclusive):
        self.__exclusive = exclusive
    
    def set_urn(self, urn):
        self.__urn = urn
    
    def set_uuid(self, uuid):
        self.__uuid = uuid
    
    def set_status(self, status):
        self.__status = status
    
    def __str__(self):
        to_return = self.__class__.__name__ + " [ "
        for attr in self.__dict__.keys():
            new_attr = attr + "=" + str(getattr(self, attr)) + ", "
            to_return += new_attr
        to_return += "]"
        return to_return
    
    def __repr__(self):
        return self.__str__()

