class Aggregate:
    
    def __init__(self):
        self.__component_id = None
        self.__component_manager_id = None
        self.__authority_urn = None
        self.__slices = list()
    
    def get_component_manager_id(self):
        return self.__component_manager_id
    
    def get_authority_urn(self):
        return self.__authority_urn
    
    def get_slices(self):
        return self.__slices
    
    def set_component_manager_id(self, value):
        self.__component_manager_id = value
    
    def set_authority_urn(self, value):
        self.__authority_urn = value
    
    def set_slices(self, value):
        self.__slices = value
    
    def __str__(self):
        to_return = self.__class__.__name__ + " [ "
        for attr in self.__dict__.keys():
            new_attr = attr + "=" + str(getattr(self, attr)) + ", "
            to_return += new_attr
        to_return += "]"
        return to_return
    
    def __repr__(self):
        return self.__str__()

