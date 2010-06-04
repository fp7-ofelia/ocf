'''
Created on Jun 8, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url, include

from views import test_view_x2, test_view_crud

urlpatterns = patterns("",
    (r"^permissions/", include("expedient.common.permissions.urls")),
    url(r"^tests/test_view_crud/$", test_view_crud, name="test_view_crud"),
    url(r"^tests/test_view_crud/(?P<obj_id>\d+)/$", test_view_crud, name="test_view_update"),
    url(r"^tests/test_view_x2/(?P<obj_id>\d+)/$", test_view_x2, name="test_view_x2"),
)
