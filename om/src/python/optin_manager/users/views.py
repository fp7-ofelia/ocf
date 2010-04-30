from django.shortcuts import render_to_response
from optin_manager.users.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.http import *

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/dashboard')
    else:
        return HttpResponseRedirect('/accounts/login')

@login_required
def dashboard(request):
    profile = UserProfile.get_or_create_profile(request.user)
    username = profile.user.username
    return render_to_response('dashboard.html', {'profile': profile, 'username': username})

