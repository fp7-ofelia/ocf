
class PolicyManager():
    
    #TODO: Implement real policies, probably a Policy model should be created

    @staticmethod
    def checkPolicies(action):
     
        if action.type_ == 'create':
            #if PolicyManager.checkPoliciesVM(action.virtual_machine):
            return True
        

        if action.type_ == 'hardStop':
            return True

        if action.type_ == 'delete':
            return True

        if action.type_ == 'modify':
            return True

        if action.type_ == 'reboot':
            return True
        
        if action.type_ == 'start':
            return True
        

    @staticmethod
    def checkPoliciesVM(vm):
        if vm.xen_configuration.memory_mb < 2001:
            print vm.xen_configuration.memory_mb
            return True

