from django.shortcuts import render_to_response
from models import UserProfile
from django.contrib.auth.decorators import login_required
from django.http import *
from django.http import HttpResponse
from django.views.generic import simple
from openflow.optin_manager.opts.models import AdminFlowSpace, UserFlowSpace
from openflow.optin_manager.admin_manager.models import *
from openflow.optin_manager.users.models import Priority

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/dashboard')
    else:
        return HttpResponseRedirect('/accounts/login')

@login_required
def dashboard(request):
    # if this the first time that admin logs in, give him all FS:
    if (request.user.is_superuser):
        p = UserProfile.get_or_create_profile(request.user)
        p.is_net_admin = True
        p.priority = Priority.Aggregate_Admin
        p.supervisor = request.user
        p.save()

        list = AdminFlowSpace.objects.filter(user=request.user)
        if len(list)==0:
            AdminFlowSpace.objects.create(user=request.user)
    
    profile = UserProfile.get_or_create_profile(request.user)
    username = profile.user.username
    
    next_steps = []
#    if (not profile.is_net_admin):
#        ufs = UserFlowSpace.objects.filter(user=request.user)
#        if (len(ufs) == 0):
#            rufs = RequestedUserFlowSpace.objects.filter(user=request.user)
#        else:
#            next_steps.append("")
    
    return simple.direct_to_template(request, 
                            template = 'openflow/optin_manager/dashboard.html',
                            extra_context = {
                                    'user':request.user,
                                    'profile': profile, 
                                    'username': username,
                                    'next_steps':next_steps,
                            },
                        )
