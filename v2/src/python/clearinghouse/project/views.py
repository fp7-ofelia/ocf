'''
@author: jnaous
'''

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from django.contrib import auth
import models

def detail(request, proj_id):
    '''Show information about the project and functions'''
    
    project = get_object_or_404(models.Project, pk=proj_id)
    