from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.views.generic import simple
from vt_manager.controller.users.forms import *
from django.contrib.auth.forms import PasswordChangeForm
from vt_manager.controller.drivers.VTDriver import VTDriver

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
	if request.method == "GET":
		user_form = UserForm(instance=request.user)
		pass_change_form = PasswordChangeForm(request.user)
    
	elif request.method == "POST":
		user_form = UserForm(request.POST, instance=request.user)
		valid1 = user_form.is_valid()
        
		if (request.POST['old_password']!=""):
			pass_change_form = PasswordChangeForm(request.user, request.POST)
			valid2 = pass_change_form.is_valid()
		else:
			pass_change_form = PasswordChangeForm(request.user)
			valid2 = True
            
		if (valid1 and valid2):
			user_form.save()
			if (request.POST['old_password']!=""):
				pass_change_form.save()
            
			return HttpResponseRedirect("/dashboard")
            
	else:
		return HttpResponseNotAllowed("GET", "POST")
    

	if (request.user.is_superuser):
		return simple.direct_to_template(request, 
			template = 'users/change_profile_admin.html',
			extra_context = {
				'user_form':user_form,
				'pass_form':pass_change_form,
			}
		)
	else:
		return HttpResponseRedirect('/accounts/login')
#		return simple.direct_to_template(request, 
#			template = 'users/change_profile_user.html',
#			extra_context = {
#				'user_form':user_form,
#				'pass_form':pass_change_form,
#			}
#		)  


@login_required
def dashboard(request):
	'''
	The dashboard view function
	'''
    
	if (not request.user.is_superuser):
		return HttpResponseRedirect('/accounts/login')        
   
	else: #Admin
        
		servers = VTDriver.getAllServers()
            
		return simple.direct_to_template(request, 
							template = 'dashboard_admin.html',
							extra_context = {
							'user': request.user,
							'servers' : servers,
							},
						)
