from rspecs.src.geni.v3.container.sliver import Sliver

class FlowSpace(Sliver):
    
    def __init__(self):
        self.__email = None
        self.__description = None
        self.__controller = None
        self.__groups = list()