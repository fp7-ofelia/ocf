'''
Created on Jun 19, 2010

@author: jnaous
'''

from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from expedient.common.permissions.shortcuts import has_permission 
from django.contrib.auth.models import User

def home(request):
    return direct_to_template(
        request,
        template='expedient/clearinghouse/index.html',
        extra_context={
            "breadcrumbs": (
                ("Home", reverse("home")),
            ),
        }
    )
