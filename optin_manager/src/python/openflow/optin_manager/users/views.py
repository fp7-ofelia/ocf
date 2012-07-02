from django.shortcuts import render_to_response
from models import UserProfile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.views.generic import simple
from openflow.optin_manager.opts.models import UserFlowSpace, UserOpts, OptsFlowSpace, AdminFlowSpace
from openflow.optin_manager.admin_manager.models import *
from openflow.optin_manager.users.forms import *
from django.contrib.auth.forms import PasswordChangeForm

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/dashboard')
    else:
        return HttpResponseRedirect('/accounts/login')

@login_required
def change_profile(request):
    '''
    The view function to change profile information for a user or admin.
    '''
    profile = UserProfile.get_or_create_profile(request.user)
    if request.method == "GET":
        user_form = UserForm(instance=request.user)
        pass_change_form = PasswordChangeForm(request.user)
        if profile.is_net_admin:
            admin_form = AdminProfileForm(instance=request.user.get_profile())
    elif request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        valid1 = user_form.is_valid()
        
        if profile.is_net_admin:
            admin_form = AdminProfileForm(request.POST, instance=request.user.get_profile())
            valid3 = admin_form.is_valid()
        else:
            valid3 = True
        
        if (request.POST['old_password']!=""):
            pass_change_form = PasswordChangeForm(request.user, request.POST)
            valid2 = pass_change_form.is_valid()
        else:
            pass_change_form = PasswordChangeForm(request.user)
            valid2 = True
            
        if (valid1 and valid2 and valid3):
            user_form.save()
            if (request.POST['old_password']!=""):
                pass_change_form.save()
            if profile.is_net_admin:
                admin_form.save()
            
            return HttpResponseRedirect("/dashboard")
            
    else:
        return HttpResponseNotAllowed("GET", "POST")
    

    if (profile.is_net_admin):
        return simple.direct_to_template(request, 
            template = 'openflow/optin_manager/users/change_profile_admin.html',
            extra_context = {
                'user_form':user_form,
                'pass_form':pass_change_form,
                'admin_form':admin_form
            }
        )
    else:
        return simple.direct_to_template(request, 
            template = 'openflow/optin_manager/users/change_profile_user.html',
            extra_context = {
                'user_form':user_form,
                'pass_form':pass_change_form,
            }
        )  

@login_required
def dashboard(request):
    '''
    The dashboard view function
    '''
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
        adminfs = AdminFlowSpace.objects.filter(user=request.user)
        
        opts = UserOpts.objects.filter(user=request.user).order_by('-priority')
        optsfs = []
        for opt in opts:
            fses = opt.optsflowspace_set.all()
            for fs in fses:
                optsfs.append(fs)
                
        num_user_reqs = RequestedUserFlowSpace.objects.filter(admin=request.user).count()
        num_admin_reqs = RequestedAdminFlowSpace.objects.filter(admin=request.user).count()
        num_admin_promotes = AdminPromoteRequest.objects.filter(admin=request.user).count()
        return simple.direct_to_template(request, 
                            template = 'openflow/optin_manager/dashboard_admin.html',
                            extra_context = {
                                    'user': request.user,
                                    'optsfs': optsfs,
                                    'adminfs': adminfs,
                                    'num_admin_reqs': num_admin_reqs,
                                    'num_user_reqs': num_user_reqs,
                                    'num_admin_promotes': num_admin_promotes,
                            },
                        )