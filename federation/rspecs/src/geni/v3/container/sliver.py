class Sliver:
    
    def __init__(self):
        self.__name = None
        self.__resources = None
        self.__urn = None
        self.__expires = None
        self.__operational_state = None
        self.__allocation_state = None
        self.__get_client_id = None
    
    def get_allocation_state(self):
        return self.__allocation_state
    
    def set_allocation_state(self, value):
        self.__allocation_state = value
    
    def get_name(self):
        return self.__name
    
    def get_resources(self):
        return self.__resources
    
    def get_urn(self):
        return self.__urn
    
    def get_expires(self):
        return self.__expires
    
    def get_operational_state(self):
        return self.__operational_state
    
    def set_name(self, value):
        self.__name = value
    
    def set_resources(self, value):
        self.__resources = value
    
    def set_urn(self, value):
        self.__urn = value
    
    def set_expires(self, value):
        self.__expires = value
    
    def set_operational_state(self, status):
        self.__operational_state = status
    
    def __str__(self):
        to_return = self.__class__.__name__ + " [ "
        for attr in self.__dict__.keys():
            new_attr = attr + "=" + str(getattr(self, attr)) + ", "
            to_return += new_attr
        to_return += "]"
        return to_return
    
    def __repr__(self):
        return self.__str__()

