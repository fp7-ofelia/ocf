'''
Created on Jul 29, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns("expedient.clearinghouse.roles.views",
    url(r"^confirm/(?P<proj_id>\d+)/(?P<req_id>\d+)/(?P<allow>\d)/(?P<delegate>\d)/$", "confirm_request", name="roles_confirm_request"),
    url(r"^create/(?P<proj_id>\d+)/$", "create", name="roles_create"),
    url(r"^update/(?P<role_id>\d+)/$", "update", name="roles_update"),
    url(r"^delete/(?P<role_id>\d+)/$", "delete", name="roles_delete"),
)
