class Resource:
    
    def __init__(self):
        self.__id = None
        self.__uuid = None
        self.__allocation_state = None
        self.__operational_state = None
        self.__sliver = None
        self.__component_id = None
        self.__component_name = None
        self.__component_manager_id = None
        self.__component_manager_name = None
        self.__available = None
        self.__exclusive = None
        self.__type = None
        self.__error_message = None
    
    def get_id(self):
        return self.__id
    
    def get_uuid(self):
        return self.__uuid

    def get_allocation_state(self):
        return self.__allocation_state

    def get_operational_state(self):
        return self.__operational_state

    def get_sliver(self):
        return self.__sliver

    def get_component_id(self):
        return self.__component_id

    def get_component_name(self):
        return self.__component_name

    def get_component_manager_id(self):
        return self.__component_manager_id

    def get_component_manager_name(self):
        return self.__component_manager_name

    def get_available(self):
        return self.__available

    def get_exclusive(self):
        return self.__exclusive
    
    def get_type(self):
        return self.__type

    def get_error_message(self):
        return self.__error_message

    def set_id(self, value):
        self.__id = value

    def set_uuid(self, value):
        self.__uuid = value

    def set_allocation_state(self, value):
        self.__allocation_state = value

    def set_operational_state(self, value):
        self.__operational_state = value

    def set_sliver(self, value):
        self.__sliver = value

    def set_component_id(self, value):
        self.__component_id = value

    def set_component_name(self, value):
        self.__component_name = value

    def set_component_manager_id(self, value):
        self.__component_manager_id = value

    def set_component_manager_name(self, value):
        self.__component_manager_name = value

    def set_available(self, value):
        self.__available = value

    def set_exclusive(self, value):
        self.__exclusive = value
        
    def set_type(self, value):
        self.__type = value

    def set_error_message(self, value):
        self.__error_mesage = value
        
#    def add_sliver(self, value):
#        if not type(self.__slivers) == list:
#            self.__slivers = [value]
#        else:
#            self.__slivers.append(value)
        
    def __str__(self):
        to_return = self.__class__.__name__ + " [ "
        attrs = self.__dict__.keys()
        attrs.sort()
        for attr in attrs:
            new_attr = attr + "=" + str(getattr(self, attr)) + ", "
            to_return += new_attr
        to_return += "]"
        return to_return
    
    def __repr__(self):
        return self.__str__()
