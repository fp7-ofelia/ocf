'''
Created on Dec 3, 2009

@author: jnaous
'''

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from expedient.clearinghouse import users
from expedient.clearinghouse.users import forms
from django.views.generic import create_update
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
        
    return render_to_response('expedient/clearinghouse/users/home.html',
                              {'user_list': user_list,
                               'pwd_form': pwd_form,
                               'user_form': user_form,
                               'userprofile_form': userprofile_form,
                               })

def detail(request, user_id=None):
    # TODO: This needs a lot of security. Users should not be able to change
    #       all the stuff in their profiles
    if user_id == None:
        user = request.user
    else:
        user = get_object_or_404(auth.models.User, pk=user_id)
    
    profile = users.models.UserProfile.get_or_create_profile(user)
    
    if request.method == "GET":
        if user_id == None:
            pwd_form = users.forms.PasswordChangeFormDisabled(user)
        else:
            pwd_form = users.forms.AdminPasswordChangeFormDisabled(user)
        
        user_form = users.forms.UserForm(instance=user)
        userprofile_form = users.forms.UserProfileForm(instance=profile)
        
    elif request.method == "POST":
        if user_id == None:
            pwd_form = users.forms.PasswordChangeFormDisabled(user, request.POST)
        else:
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

    try:
        slice_set = user.slice_set.all()
    except AttributeError:
        slice_set = ()
    
    return render_to_response("expedient/clearinghouse/users/detail.html",
                              {'user': user,
                               'slices': slice_set,
                               'pwd_form': pwd_form,
                               'user_form': user_form,
                               'show_owner': True,
                               'userprofile_form': userprofile_form,
                               })

def saved(request, user_id):
    user = get_object_or_404(auth.models.User, pk=user_id)

    return render_to_response("expedient/clearinghouse/users/saved.html",
                              {'user': user},
                              )

def delete(request, user_id):
    return create_update. \
            delete_object(request,
                          auth.models.User,
                          reverse("users_home"),
                          user_id,
                          template_name="expedient/clearinghouse/users/confirm_delete.html")
