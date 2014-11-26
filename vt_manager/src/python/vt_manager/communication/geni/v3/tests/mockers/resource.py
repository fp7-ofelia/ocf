class ResourceMocker:
    def __init__(self):
        self.component_id = None
        self.operational_state = None

    def get_component_id(self):
        return self.component_id

    def set_component_id(self, value):
        self.component_id = value 

    def get_operational_state(self):
        return self.operational_state

    def set_operational_state(self, value):
        self.operational_state = value 
