'''
Created on Jun 6, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns("expedient.common.permissions.views",
    url(r"^(?P<perm_name>\w+)/(?P<target_ct_id>\d+)/(?P<target_id>\d+)/(?P<permittee_ct_id>\d+)/(?P<permittee_id>\d+)/$", "redirect_permissions_request", name="permissions_url"),
    url(r"^(?P<perm_name>\w+)/(?P<target_ct_id>\d+)/(?P<target_id>\d+)/(?P<permittee_ct_id>\d+)/(?P<permittee_id>\d+)/$", "reraise_permission_denied", name="permissions_reraise"),
)
