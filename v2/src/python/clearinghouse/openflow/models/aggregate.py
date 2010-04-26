'''
@author: jnaous
'''

import os
from django.db import models
from clearinghouse.aggregate import models as aggregate_models

class OpenFlowAdminInfo(aggregate_models.AggregateAdminInfo):
    pass

class OpenFlowUserInfo(aggregate_models.AggregateUserInfo):
    pass

class OpenFlowSliceInfo(aggregate_models.AggregateSliceInfo):
    def get_rpc_info(self):
        '''
        Get the information about the slice to use in XML-RPC with AM.
        
        @return {'id': self.slice.id, 'name': self.slice.name,
                 'description': self.slice.description}
        '''
        
        return {'id': self.slice.id, 'name': self.slice.name,
                'description': self.slice.description}
        
    def get_switches_info(self):
        '''
        Get the information about switches in the topology to
        use in XML-RPC with the AM. For each switch in the topology
        of the aggregate, returns a dict that has the following keys.
        
        - C{dpid}: the switch's datapath id
        - C{flowspace}: an array of dicts describing the switch's flowspace
            Each such dict has the following keys:
                - C{port}: the port for this flowspace
                - C{direction}: 'ingress', 'egress', or 'bidirectional'
                - C{policy}: 1 for 'allow', -1 for 'deny', 0 for read only
                - C{dl_src}: link layer address in "xx:xx:xx:xx:xx:xx" format
                    or '*' for wildcard
                - C{dl_dst}: link layer address in "xx:xx:xx:xx:xx:xx" format
                    or '*' for wildcard
                - C{vlan_id}: vlan id as an int or -1 for wildcard
                - C{nw_src}: network address in "x.x.x.x" format
                    or '*' for wildcard
                - C{nw_dst}: network address in "x.x.x.x" format
                    or '*' for wildcard
                - C{nw_proto}: network protocol as an int or -1 for wildcard
                - C{tp_src}: transport port as an int or -1 for wildcard
                - C{tp_dst}: transport port as an int or -1 for wildcard
        
        @return returns an array of dicts with information for each switch
        '''
        pass
#        ret = []
#        for sw in self.slice.openflowswitchsliver_set.\
#        filter(switch__aggregate=self):
#            d = {'dpid': sw.switch.datapath_id}
#            fs_set = []
#            for fs in sw.flowspace_set.all():
#                fs_set = fs_set.append({
#                    'port': fs.interface.
#                })
            

class OpenFlowProjectInfo(aggregate_models.AggregateProjectInfo):
    pass

class OpenFlowAggregate(aggregate_models.Aggregate):
    password = models.CharField(max_length=1024,
                                default=lambda: os.urandom(1024))
    max_password_age = models.IntegerField(
        help_text='Maximum age of password in days', default=60)
    password_timestamp = models.DateTimeField(auto_now_add=True)
    url = models.URLField(max_length=1024, verify_exists=True)
    
    class Extend:
        replacements= {
            'admin_info_class': OpenFlowAdminInfo,
            'user_info_class': OpenFlowUserInfo,
            'slice_info_class': OpenFlowSliceInfo,
            'project_info_class': OpenFlowProjectInfo,
        }
    
    def get_server_instance(self):
        from xmlrpclib import ServerProxy
        from clearinghouse.utils import PyCURLSafeTransport
        return ServerProxy(self.url, ) #TODO Finish this
    
    def update_slice(self, slice, server=None):
        server = server or self.get_server_instance()
        self.delete_slice(self, slice, server)
        self.reserve_slice(self, slice, server)
        
    def reserve_slice(self, slice, server=None):
        server = server or self.get_server_instance()
        # get all the slivers that are in this aggregate
        switch_slivers = slice.openflowswitchsliver_set.filter(switch__aggregate=self)
        link_slivers = slice.openflowswitchsliver_set.filter(switch__aggregate=self)
        
        # send each switch sliver as a dict/struct
        switches = []
        
        # get the connection to the server
#        am_server = ServerProxy(self.url)
#        am_server.reserve_slice()
        
    def delete_slice(self, slice, server=None):
        pass
