class Element(dict):

    fields = {}

    def __init__(self, fields={}, element=None, keys=None):
        self.element = element
        dict.__init__(self, dict.fromkeys(self.fields))
        if not keys:
            keys = fields.keys()
        for key in keys:
            if key in fields:
                self[key] = fields[key] 


    def __getattr__(self, name):
        if hasattr(self.__dict__, name):
            return getattr(self.__dict__, name)
        elif hasattr(self.element, name):
            return getattr(self.element, name)
        else:
            raise AttributeError, "class Element has no attribute %s" % name
