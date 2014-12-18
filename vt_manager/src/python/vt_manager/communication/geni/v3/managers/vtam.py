from am.ambase.src.abstract.classes.resourcemanagerbase import ResourceManagerBase
from vt_manager.communication.geni.v3.drivers.vtam import VTAMDriver

class VTAMRM(ResourceManagerBase):

    def __init__(self):
        self.__driver = VTAMDriver()
        self.START_ACTION = "START"
        self.STOP_ACTION = "STOP"
        self.REBOOT_ACTION = "REBOOT"
        self.DELETE_ACTION = "DELETE"

    def get_version(self):
        return {} 

    def get_resources(self, urns=None, geni_available=False):
        servers = list()
        if urns:
            for urn in urns:
                server = self.__driver.get_specific_server_and_vms(urn, geni_available)
                if type(server) == list:
                    servers.extend(server)
                else:
                    servers.append(server)
            return servers
        else:
            servers = self.__driver.get_all_servers(geni_available)
            return servers
    
    def create_resources(self, urns, expiration=None, users=list(), geni_best_effort=False):
        created_resources = list()
        for urn in urns:
            resource = self.__driver.create_vms(urn, expiration, users, geni_best_effort)
            if type(resource) == list:
                created_resources.extend(resource)
            else:
                created_resources.append(resource)
        return created_resources
    
    def reserve_resources(self, slice_urn, reservations, expiration=None, users=list()):
        reserved_resources = list()
        for r in reservations:
            reserved_resource = self.__driver.reserve_vms(slice_urn, r, expiration, users)
            if type(reserved_resource) == list():
                reserved_resources.extend(reserved_resource)
            else:
                reserved_resources.append(reserved_resource)
        #reserved_resources =  self.__update_reservation(reserved_resources)  #TODO
        return reserved_resources
    
    def delete_resources(self, urns, geni_best_effort=False):
        return self.__crud_resources(urns, geni_best_effort, self.DELETE_ACTION)
    
    def start_resources(self, urns, geni_best_effort=False):
        return self.__crud_resources(urns, geni_best_effort, self.START_ACTION)
    
    def stop_resources(self, urns, geni_best_effort=False):
        return self.__crud_resources(urns, geni_best_effort, self.STOP_ACTION) 
    
    def reboot_resources(self, urns, geni_best_effort=False):
        return self.__crud_resources(urns, geni_best_effort, self.REBOOT_ACTION)
    
    def update_resources_users(self, urns, geni_best_effort=False, options=dict()):
        """
        geni_update_users: Refresh the set of user accounts and installed SSH keys on the resource.
            Takes the option geni_users. This action creates any users specified that do not already 
                                         exist, and sets the SSH keys for all users per the list of 
                                         keys specified - including removing keys not explicitly 
                                         listed. The geni_users option can be supplied using the 
                                         --optionsfile argument.
                             If not supplied that way, then users are read from the omni_config or 
                             clearinghouse slice members, as documented under createsliver.
           
            Note: the --optionsfile argument requires a file. Expected format:
                    {
                     "geni_users": [
                      {
                       "urn": "urn:publicid:IDN+ch.geni.net+user+jdoe",
                       "keys": ["ssh-rsa jdoegoodkey"]
                      },
                      {
                       "urn": "urn:publicid:IDN+ch.geni.net+user+jsmith",
                       "keys": ["somekey", "someotherkey"]
                      }
                     ]
                    }
        """
        
        # NOTE that the user and keys can be passed in two ways:
        #    a) the '--optionsfile' option
        #    b) directly read from the OMNI config file
        # In any case, both will be available under 'options["geni_users"]'
        geni_users = options.get("geni_users", None)
        if not geni_users:
            # This translates into a BADARGS exception in the handler
            raise Exception("Missing user and keys (maybe config file not present, or --optionsfile argument not present")
        return self.__driver.update_keys(urns, geni_users, geni_best_effort)
    
    def cancel_update_resources_users(self, urns, geni_best_effort=False):
        return self.__driver.cancel_update_keys(urns, geni_best_effort)
     
    def retrieve_resources_url(self, urns, geni_best_effort=False):
        """
        Return URI or way to access the VM.
        """
        return self.__driver.retrieve_access_data(urns, geni_best_effort)
    
    def renew_resources(self, urns, expiration, geni_best_effort=False):
        resources = list()
        self.__driver.set_geni_best_effort_mode(geni_best_effort)
        for urn in urns:
            try:
                resource = self.__driver.renew_vms(urn, expiration)
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
                resource = self.__driver.start_vm(urn)
            elif action == self.STOP_ACTION:
                resource = self.__driver.stop_vm(urn)
            elif action == self.REBOOT_ACTION:
                resource = self.__driver.reboot_vm(urn)
            elif action == self.DELETE_ACTION:
                resource = self.__driver.delete_vm(urn)
            if type(resource) == list:
                resources.extend(resource)
            else:
                resources.append(resource)
        return resources

    def get_driver(self):
        return self.__driver

    def set_driver(self, value):
        self.__driver = value     
        
