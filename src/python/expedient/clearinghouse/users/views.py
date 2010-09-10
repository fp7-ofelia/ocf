'''
Created on Dec 3, 2009

@author: jnaous
'''

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from expedient.clearinghouse import users
from django.views.generic import create_update, simple
from django.contrib import auth
from expedient.common.permissions.shortcuts import must_have_permission,\
    give_permission_to
from registration import views as registration_views
from expedient.clearinghouse.users.forms import FullRegistrationForm
from registration.models import RegistrationProfile
from django.conf import settings
from django.contrib.auth.models import User

def home(request):
    '''show list of users and form for adding users'''
    
    must_have_permission(request.user, User, "can_manage_users")
    
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
            up = users.models.UserProfile(user=user)
            userprofile_form = users.forms.UserProfileForm(request.POST, instance=up)
            userprofile_form.save()
            return HttpResponseRedirect(reverse("users_saved", args=(user.id,)))
        
    else:
        return HttpResponseNotAllowed("GET", "POST")
        
    return simple.direct_to_template(
        request,
        template='expedient/clearinghouse/users/home.html',
        extra_context={
            'user_list': user_list,
            'pwd_form': pwd_form,
            'user_form': user_form,
            'userprofile_form': userprofile_form,
        },
    )

def detail(request, user_id=None):
    if user_id == None:
        user = request.user
    else:
        user = get_object_or_404(auth.models.User, pk=user_id)

    must_have_permission(request.user, user, "can_edit_user")
    
    profile = users.models.UserProfile.get_or_create_profile(user)
    
    if request.method == "GET":
        if user_id == None:
            pwd_form = users.forms.PasswordChangeFormDisabled(user)
        else:
            pwd_form = users.forms.AdminPasswordChangeFormDisabled(user)
        
        user_form = users.forms.UserForm(instance=user)
        userprofile_form = users.forms.UserProfileForm(instance=profile)
        
    elif request.method == "POST":
        if request.POST.get("change_pwd", False):
            data = request.POST
        else:
            data = None
        if user_id == None:
            pwd_form = users.forms.PasswordChangeFormDisabled(user, data)
        else:
            pwd_form = users.forms.AdminPasswordChangeFormDisabled(user, data)
        user_form = users.forms.UserForm(request.POST, instance=user)
        userprofile_form = users.forms.UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and userprofile_form.is_valid():
            user = user_form.save()
            userprofile_form = users.forms.UserProfileForm(request.POST, instance=profile)
            userprofile_form.save()
            if request.POST.get("change_pwd", False) and pwd_form.is_valid():
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
    
    return simple.direct_to_template(
        request,
        template='expedient/clearinghouse/users/detail.html',
        extra_context={
            'user': user,
            'slices': slice_set,
            'pwd_form': pwd_form,
            'user_form': user_form,
            'show_owner': True,
            'userprofile_form': userprofile_form,
            'breadcrumbs': (
                ("Home", reverse("home")),
                ("Account for %s" % user.username, reverse("users_detail", args=[user.id])),
            )
        },
    )

def saved(request, user_id):
    user = get_object_or_404(auth.models.User, pk=user_id)

    return simple.direct_to_template(
        request,
        template='expedient/clearinghouse/users/saved.html',
        extra_context={
            'user': user,
        },
    )

def delete(request, user_id):
    user = get_object_or_404(auth.models.User, pk=user_id)
    must_have_permission(request.user, user, "can_edit_user")
    return create_update.delete_object(
        request,
        auth.models.User,
        reverse("users_home"),
        user_id,
        template_name="expedient/clearinghouse/users/confirm_delete.html",
    )

def register(request):
    return registration_views.register(
        request,
        form_class=FullRegistrationForm)

def activate(request, activation_key):
    template_name = 'registration/activate.html'
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    account = RegistrationProfile.objects.activate_user(activation_key)
    if account:
        give_permission_to(
            "can_edit_user", account, account, can_delegate=True)
    return simple.direct_to_template(
        request,
        template=template_name,
        extra_context={
            'account': account,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
        },
    )

