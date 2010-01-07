'''
Created on Dec 3, 2009

@author: jnaous
'''

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from clearinghouse import users
import forms
from django.views import generic
from django.contrib import auth

def home(request):
    '''show list of users and form for adding users'''
    
    user_list = auth.models.User.objects.all()
    
    if request.method == "GET":
        pwd_form = auth.forms.UserCreationForm()
        user_form = users.forms.UserForm()
        userprofile_form = users.forms.UserProfileForm()
        
    elif request.method == "POST":
        pwd_form = auth.forms.UserCreationForm(request.POST)
        user_form = users.forms.UserForm(request.POST)
        userprofile_form = users.forms.UserProfileForm(request.POST)
        # check that all data is valid
        if pwd_form.is_valid() and user_form.is_valid() and userprofile_form.is_valid():
            # create the user first
            user = pwd_form.save()
            # use the user to save the user info
            user_form = users.forms.UserForm(request.POST, instance=user)
            user = user_form.save()
            # now store the user profile
            up = users.models.UserProfile(user=user, created_by=request.user)
            userprofile_form = users.forms.UserProfileForm(request.POST, instance=up)
            userprofile_form.save()
            return HttpResponseRedirect(reverse("users_saved", args=(user.id,)))
        
    else:
        return HttpResponseNotAllowed("GET", "POST")
        
    return render_to_response('users/home.html',
                              {'user_list': user_list,
                               'pwd_form': pwd_form,
                               'user_form': user_form,
                               'userprofile_form': userprofile_form,
                               })

def detail(request, user_id):
    user = get_object_or_404(auth.models.User, pk=user_id)
    
    profile = users.models.UserProfile.get_or_create_profile(user)
    
    if request.method == "GET":
        pwd_form = users.forms.AdminPasswordChangeFormDisabled(user)
        user_form = users.forms.UserForm(instance=user)
        userprofile_form = users.forms.UserProfileForm(instance=profile)
        
    elif request.method == "POST":
        pwd_form = users.forms.AdminPasswordChangeFormDisabled(user, request.POST)
        user_form = users.forms.UserForm(request.POST, instance=user)
        userprofile_form = users.forms.UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and userprofile_form.is_valid():
            user = user_form.save()
            userprofile_form = users.forms.UserProfileForm(request.POST, instance=profile)
            userprofile_form.save()
            if "change_pwd" in request.POST and pwd_form.is_valid():
                pwd_form.save()
                return HttpResponseRedirect(reverse("users_saved", args=(user.id,)))
            elif "change_pwd" not in request.POST:
                return HttpResponseRedirect(reverse("users_saved", args=(user.id,)))
    else:
        return HttpResponseNotAllowed("GET", "POST")

    return render_to_response("users/detail.html",
                              {'user': user,
                               'slices': user.slice_set.all(),
                               'pwd_form': pwd_form,
                               'user_form': user_form,
                               'show_owner': True,
                               'userprofile_form': userprofile_form,
                               })
    
def saved(request, user_id):
    user = get_object_or_404(auth.models.User, pk=user_id)

    return render_to_response("users/saved.html",
                              {'user': user},
                              )

def delete(request, user_id):
    return generic.create_update. \
            delete_object(request,
                          auth.models.User,
                          reverse("users_home"),
                          user_id,
                          template_name="users/confirm_delete.html")
