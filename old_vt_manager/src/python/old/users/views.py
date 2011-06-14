from django.shortcuts import render_to_response
from models import UserProfile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.views.generic import simple
#from vt_manager.opts.models import UserFlowSpace, UserOpts, OptsFlowSpace, AdminFlowSpace
#from vt_manager.admin_manager.models import *
from vt_manager.users.forms import *
from django.contrib.auth.forms import PasswordChangeForm
from vt_manager.models import *

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
            template = 'users/change_profile_admin.html',
            extra_context = {
                'user_form':user_form,
                'pass_form':pass_change_form,
                'admin_form':admin_form
            }
        )
    else:
        return simple.direct_to_template(request, 
            template = 'users/change_profile_user.html',
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
    saludo = "Como te baila?"
    profile = UserProfile.get_or_create_profile(request.user)    
    
    if (not profile.is_net_admin):
           
        return simple.direct_to_template(request, 
                            template = 'dashboard_user.html',
                            extra_context = {
                                    'user':request.user,
                                    'test_param':"user resfriado",
                            },
                        )
    else: #Admin
        
        return simple.direct_to_template(request, 
                            template = 'dashboard_admin.html',
                            extra_context = {
                                   'user': request.user,
                                    'test_param': "admin resfriado",
                				    'saludo': saludo,
                            },
                        )
