from django.shortcuts import render_to_response
from models import UserProfile
from django.contrib.auth.decorators import login_required
from django.http import *
from django.http import HttpResponse
from django.views.generic import simple
from openflow.optin_manager.opts.models import AdminFlowSpace, UserFlowSpace, UserOpts
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
    
    if (not profile.is_net_admin):
        next_steps = 0
        opts = []
        ufs = UserFlowSpace.objects.filter(user=request.user)
        if (len(ufs) == 0):
            rufs = RequestedUserFlowSpace.objects.filter(user=request.user)
            if (len(rufs) == 0):
                next_steps = 0
            else:
                next_steps = 1
        else:
            opts = UserOpts.objects.filter(user=request.user).order_by('-priority')
            if (len(opts) == 0):
                next_steps = 2
            else:
                next_steps = 3
    
        return simple.direct_to_template(request, 
                            template = 'openflow/optin_manager/dashboard_user.html',
                            extra_context = {
                                    'user':request.user,
                                    'next_steps':next_steps,
                                    'opts': opts,
                            },
                        )
    else: #Admin
        
        return simple.direct_to_template(request, 
                            template = 'openflow/optin_manager/dashboard_admin.html',
                            extra_context = {
                                    'user':request.user,
                            },
                        )