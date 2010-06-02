'''
Created on Jun 2, 2010

@author: jnaous
'''

from expedient.common.permissions.utils import register_controlled_type,\
    register_permission
from django.core.urlresolvers import reverse

register_permission("can_create_openflow_sliver",
                    url_name="get_openflow_create_permission")
register_permission("can_delete_openflow_sliver",
                    url_name="get_openflow_delete_permission")
register_permission("can_admin_openflow_aggregate",
                    url_name="get_openflow_aggregate_admin_permission")
