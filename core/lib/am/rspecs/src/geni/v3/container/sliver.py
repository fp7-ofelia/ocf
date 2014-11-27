class Sliver:
    
    def __init__(self):
        self.__urn = None
        self.__name = None
        self.__slice_urn = None
        self.__allocation_status = None
        self.__operational_status = None
        self.__expiration = None
        self.__resource = None
        self.__type = None
        self.__services = list()
        self.__client_id = None

    def get_urn(self):
        return self.__urn

    def get_name(self):
        return self.__name

    def get_slice_urn(self):
        return self.__slice_urn

    def get_allocation_status(self):
        return self.__allocation_status

    def get_operational_status(self):
        return self.__operational_status

    def get_expiration(self):
        return self.__expiration

    def get_resource(self):
        return self.__resource

    def get_type(self):
        return self.__type

    def get_services(self):
        return self.__services

    def get_client_id(self):
        return self.__client_id

    def set_urn(self, value):
        self.__urn = value

    def set_name(self, value):
        self.__name = value

    def set_slice_urn(self, value):
        self.__slice_urn = value

    def set_allocation_status(self, value):
        self.__allocation_status = value

    def set_operational_status(self, value):
        self.__operational_status = value

    def set_expiration(self, value):
        self.__expiration = value

    def set_resource(self, value):
        self.__resource = value

    def set_type(self, value):
        self.__type = value

    def set_services(self, value):
        self.__services = value

    def set_client_id(self, value):
        self.__client_id = value

    def __str__(self):
        to_return = self.__class__.__name__ + " [ "
        attrs = self.__dict__.keys()
        attrs.sort()
        for attr in attrs:
            if attr == "_Sliver__resource":
                continue
            new_attr = attr + "=" + str(getattr(self, attr)) + ", "
            to_return += new_attr
        to_return += "]"
        return to_return
    
    def __repr__(self):
        return self.__str__()       

