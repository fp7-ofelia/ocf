from am.ambase.src.abstract.classes.resourcemanagerbase import ResourceManagerBase
from openflow.optin_manager.geni.v3.drivers.optin import OptinDriver

class OptinRM(ResourceManagerBase):

    def __init__(self):
        self.__driver = OptinDriver()
        self.START_ACTION = "START"
        self.STOP_ACTION = "STOP"
        self.REBOOT_ACTION = "REBOOT"
        self.DELETE_ACTION = "DELETE"
 
    def get_version(self):
        return self.__driver.get_version()

    def get_resources(self, urns=None, geni_available=True):
        if urns:
            slivers = list()
            for urn in urns:
                 slivers.append(self.__driver.get_specific_devices(urn, geni_available))
            return slivers[0]
        else:
            return self.__driver.get_all_devices(geni_available)
    
    def create_resources(self, urns, expiration=None, users=list(), geni_best_effort=True):
        flowspaces = list()
        for urn in urns:
            flowspaces.append(self.__driver.create_flowspace(urn,expiration,users, geni_best_effort))
        return flowspaces[0]
    
    def reserve_resources(self, slice_urn, reservation, expiration=None, users=list()):
        return self.__driver.reserve_flowspace(slice_urn, reservation,users)

    def start_resources(self, urns, geni_best_effort=True):
        return self.__crud_resources(urns, geni_best_effort, self.START_ACTION)
    
    def stop_resources(self, urns, geni_best_effort):
        return self.__crud_resources(urns, geni_best_effort, self.STOP_ACTION) 
    
    def reboot_resources(self, urns, geni_best_effort):
        return self.__crud_resources(urns, geni_best_effort, self.REBOOT_ACTION)

    def delete_resources(self, urns, geni_best_effort):
        return self.__crud_resources(urns, geni_best_effort, self.DELETE_ACTION)

    def renew_resources(self, urns, expiration, geni_best_effort=False):
        resources = list()
        self.__driver.set_geni_best_effort_mode(geni_best_effort)
        for urn in urns:
            try:
                resource = self.__driver.renew_fs(urn, expiration)
            except Exception as e:
                raise e
            if type(resource) == list:
                resources.extend(resource)
            else:
                resources.append(resource)
        return resources

    def __crud_resources(self, urns, geni_best_effort, action):
        self.__driver.set_geni_best_effort_mode(geni_best_effort)
        resources = list()
        for urn in urns:
            if action == self.START_ACTION:
                resource = self.__driver.start_flow_space(urn)
            elif action == self.STOP_ACTION:
                resource = self.__driver.stop_flow_space(urn)
            elif action == self.REBOOT_ACTION:
                resource = self.__driver.reboot_flow_space(urn)
            elif action == self.DELETE_ACTION:
                resource = self.__driver.delete_flow_space(urn)
            if type(resource) == list:
                resources.extend(resource)
            else:
                resources.append(resource)
        return resources

    def get_driver(self):
        return self.__driver

    def set_driver(self, value):
        self.__driver = value     
        
