class PermissionManager:
    module = 'foam.sfa.methods'

    def check_permissions(self,method,params):
        function = self.get_method(method)
        if "self" in params.keys():
            params.pop("self", None)        
        return function(**params)

    def get_method(self, method):
        module = self.module + '.' + method
        return getattr(__import__(module, fromlist=[module]),method)

