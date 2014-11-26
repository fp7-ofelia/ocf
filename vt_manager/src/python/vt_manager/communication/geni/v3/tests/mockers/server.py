class ServerMocker:
    def __init__(self):
        self.virt_tech = None
        self.uuid = None

    def getUUID(self): 
        return self.uuid

    def getVirtTech(self):
        return self.virt_tech

    def set_virt_tech(self, value):
        self.virt_tech = value

    def set_uuid(self, uuid):
        self.uuid = uuid
    
