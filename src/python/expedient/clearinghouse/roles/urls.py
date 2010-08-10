'''
Created on Jul 29, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns("expedient.clearinghouse.roles.views",
    url(r"^confirm/(?P<proj_id>\d+)/(?P<req_id>\d+)/(?P<allow>\d)/(?P<delegate>\d)/$", "confirm_request", name="roles_confirm_request"),
)
