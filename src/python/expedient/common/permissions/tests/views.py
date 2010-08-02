'''
Created on Jun 8, 2010

Contains views for permissions tests

@author: jnaous
'''
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import create_update
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from expedient.common.permissions.utils import get_queryset_from_class
from expedient.common.permissions.utils import get_user_from_req, get_queryset
from expedient.common.permissions.shortcuts import give_permission_to
from expedient.common.permissions.decorators import require_objs_permissions_for_view
from models import PermissionTestClass

@require_objs_permissions_for_view(
    ["can_get_x2", "can_read_val"],
    get_user_from_req,
    get_queryset(PermissionTestClass, "obj_id"),
)
def test_view_x2(request, obj_id=None):
    obj = get_object_or_404(PermissionTestClass, pk=obj_id)
    return HttpResponse("%s" % obj.get_val_x2())

@require_objs_permissions_for_view(
    ["can_add"],
    get_user_from_req,
    get_queryset_from_class(PermissionTestClass),
    ["POST"],
)
def test_view_create(request):
    return create_update.create_object(
        request, PermissionTestClass,
        template_name="permissions/empty.html",
        post_save_redirect=reverse("test_view_crud"),
    )

def test_protected_url(request):
    return HttpResponse("Worked")

@require_objs_permissions_for_view(
    ["can_set_val"],
    get_user_from_req,
    get_queryset(PermissionTestClass, 'obj_id'),
    ["POST"],
)
@require_objs_permissions_for_view(
    ["can_read_val"],
    get_user_from_req,
    get_queryset(PermissionTestClass, 'obj_id'),
    ["GET"],
)
def test_view_update(request, obj_id=None):
    return create_update.update_object(
        request, PermissionTestClass,
        object_id=obj_id,
        template_name="permissions/empty.html",
        post_save_redirect=reverse("test_view_update",
                                   kwargs=dict(obj_id=obj_id)),
    )

def add_perms_view(request, permission, user, target, redirect_to=None):
    if request.method == "POST":
        give_permission_to(permission, target, user)
        redirect_to = redirect_to or reverse("test_view_crud")
        return HttpResponseRedirect(redirect_to)
    else:
        return HttpResponse(
"""
Do you want to get permissions to create PermissionTestClass instances?
<form action="" method="POST">
<input type="submit" value="Yes" />
<input type="button" value="No" onclick="document.location='%s'" />
</form>
""" % reverse("test_view_crud"))

def other_perms_view(request, permission, user, target, redirect_to=None):
    if request.method == "POST":
        give_permission_to(permission, target, user)
        redirect_to = redirect_to or reverse("test_view_crud")
        return HttpResponseRedirect(redirect_to)
    else:
        return HttpResponse(
"""
Do you want to get %s permission for obj %s?
<form action="" method="POST">
<input type="submit" value="Yes" />
<input type="button" value="No" onclick="document.location='%s'" />
</form>
""" % (permission.name, target, reverse("test_view_crud")))
