from django.shortcuts import render_to_response
from models import UserProfile
from django.contrib.auth.decorators import login_required
from django.http import *
from django.http import HttpResponse
from django.views.generic import simple

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/dashboard')
    else:
        return HttpResponseRedirect('/accounts/login')

@login_required
def dashboard(request):
    profile = UserProfile.get_or_create_profile(request.user)
    username = profile.user.username
    print "in the dashbaord call"
    return simple.direct_to_template(request, 
                            template = 'openflow/optin_manager/dashboard.html',
                            extra_context = {
                                    'profile': profile, 
                                    'username': username,
                            },
                        )
