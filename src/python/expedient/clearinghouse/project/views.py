'''
@author: jnaous
'''

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from django.contrib import auth
from clearinghouse.project.models import ProjectRole
import models

def detail(request, proj_id):
    '''Show information about the project and functions'''
    
    project = get_object_or_404(models.Project, pk=proj_id)
    user_roles = ProjectRole.objects.all.filter(
        member=request.user,
        project=project)
    user_can_mod_aggregate = user_roles.filter(
        role__in=(ProjectRole.PI,
                  ProjectRole.RESEARCHER,
                  ProjectRole.EXPERIMENTER),
        ).count() > 0
        
    user_can_mod_slice = user_can_mod_aggregate

    user_can_mod_role = user_roles.filter(
        role__in=(ProjectRole.PI,
                  ProjectRole.RESEARCHER),
        ).count() > 0
        
    