'''
Created on Jun 2, 2010

@author: jnaous
'''
from expedient.common.permissions.utils import create_permission
from expedient.common.permissions.views import request_permission
from django.core.urlresolvers import reverse

create_permission("can_add_aggregate", request_permission(reverse("home")))
create_permission("can_view_aggregate")
create_permission("can_edit_aggregate")
