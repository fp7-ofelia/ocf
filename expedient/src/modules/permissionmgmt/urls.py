'''
Created on Jul 29, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns("expedient.clearinghouse.permissionmgmt.views",
    url(r"^$", "permissions_dashboard", name="permissionmgmt_dashboard"),
    url(r"^confirm/$", "confirm_requests", name="permissionmgmt_confirm_req"),
)
