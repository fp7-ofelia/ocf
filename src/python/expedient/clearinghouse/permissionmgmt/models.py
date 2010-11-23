'''
Created on Jul 27, 2010

@author: jnaous
'''
from django.core.urlresolvers import resolve
from expedient.common.middleware.threadlocals import add_parser
from expedient.clearinghouse.project.models import Project
from expedient.clearinghouse.slice.models import Slice

def get_user(request):
    return request.user
add_parser("user", get_user)

def get_project(request):
    _, _, kwargs = resolve(request.path)
    if "proj_id" in kwargs:
        return Project.objects.get(id=kwargs["proj_id"])
    elif "slice_id" in kwargs:
        return Project.objects.get(slice__id=kwargs["slice_id"])
    elif "role_id" in kwargs:
        return Project.objects.get(projectrole__id=kwargs["role_id"])
    else:
        return None
add_parser("project", get_project)

def get_slice(request):
    _, _, kwargs = resolve(request.path)
    if "slice_id" in kwargs:
        return Slice.objects.get(id=kwargs["slice_id"])
    else:
        return None
add_parser("slice", get_slice)
