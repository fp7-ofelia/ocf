class PermissionManager:
    module = 'openflow.optin_manager.sfa.methods'

    def check_permissions(self,method,params):
        function = self.get_method(method)
        
        return function(**params)

    def get_method(self, method):
        module = self.module + '.' + method
        return getattr(__import__(module, fromlist=[module]),method)

