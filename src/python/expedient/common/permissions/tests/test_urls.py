'''
Created on Jun 8, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url, include

from views import test_view_x2, test_view_create, \
    test_view_update, test_protected_url
from ..utils import get_user_from_req, \
    get_queryset_from_class
from ..shortcuts import require_objs_permissions_for_url
from django.core.urlresolvers import reverse
from models import PermissionTestClass

urlpatterns = patterns("",
    (r"^permissions/", include("expedient.common.permissions.urls")),
    url(r"^tests/test_view_crud/$", test_view_create, name="test_view_crud"),
    url(r"^tests/test_view_crud/(?P<obj_id>\d+)/$", test_view_update, name="test_view_update"),
    url(r"^tests/test_view_x2/(?P<obj_id>\d+)/$", test_view_x2, name="test_view_x2"),
    url(r"^tests/test_protected_url/$", test_protected_url, name="test_protected_url"),
    url(r"^tests/test_request_perm/$", test_protected_url, name="test_request_perm"),
    url(r"^tests/test_allowed/$", test_protected_url, name="test_allowed"),
)

# protect the url
require_objs_permissions_for_url(
    reverse("test_protected_url"), ["can_call_protected_url"],
    get_user_from_req, get_queryset_from_class(PermissionTestClass))

# protect the url
require_objs_permissions_for_url(
    reverse("test_request_perm"), ["test_request_perm"],
    get_user_from_req, get_queryset_from_class(PermissionTestClass))
