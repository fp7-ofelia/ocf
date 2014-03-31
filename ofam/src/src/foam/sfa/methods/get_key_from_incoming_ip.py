from foam.sfa.util.method import Method
from foam.sfa.util.foam.sfa.ogging import logger

from foam.sfa.util.parameter import Parameter

class get_key_from_incoming_ip(Method):
    """
    Generate a new keypair and gid for requesting caller (component/node).     
    This is a myplc-specific API call used by component manager
    @return 1 If successful  
    """

    interfaces = ['registry']
    
    accepts = []

    returns = Parameter(int, "1 if successful, faults otherwise")
    
    def call(self):
        if hasattr(self.api.manager,'get_key_from_incoming_ip'):
            return self.api.manager.get_key_from_incoming_ip (api)
        else:
            logger.warning("get_key_from_incoming_ip not supported by registry manager")
            return 0
