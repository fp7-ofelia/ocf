#from vt_manager.communication.sfa.methods import *
import sys
class PermissionManager:
    module = 'vt_manager.communication.sfa.methods'

    def check_permissions(self,method,params):
        function = self.get_method(method)
        
        return function(**params)

    def get_method(self, method):
        module = self.module + '.' + method
        return getattr(__import__(module, fromlist=[module]),method)

