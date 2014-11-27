from rspecs.src.geni.v3.container.sliver import Sliver

class FlowSpace(Sliver):
    
    def __init__(self):
        Sliver.__init__(self)
        self.__email = None
        self.__description = None
        self.__controller = None
        self.__groups = list()
        self.__state = None

    def get_email(self):
        return self.__email


    def get_description(self):
        return self.__description


    def get_controller(self):
        return self.__controller


    def get_groups(self):
        return self.__groups
    

    def get_state(self):
        return self.__state


    def set_email(self, value):
        self.__email = value


    def set_description(self, value):
        self.__description = value


    def set_controller(self, value):
        self.__controller = value


    def set_groups(self, value):
        self.__groups = value

    
    def set_state(self, value):
        self.__state = value
    
    
    def add_group(self, value):
        self.__groups.append(value)
        
        
