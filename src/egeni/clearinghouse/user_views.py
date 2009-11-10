from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponseBadRequest,\
    HttpRequest, HttpResponseForbidden
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.core.urlresolvers import reverse
from egeni.clearinghouse.models import *
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import list_detail, create_update
from django.contrib.auth.forms import UserCreationForm

def can_access(user):
    '''Can the user access the user views?'''
    profile = UserProfile.get_or_create_profile(user)
    return user.is_staff or profile.is_user_admin

@user_passes_test(can_access)
def home(request):
    '''show list of users and form to create new one'''
    
    if request.user.is_staff:
        user_list = User.objects.all()
        UserFormCls = UserFormSU
        UserProfileFormCls = UserProfileFormSU
    else:
        user_list = User.objects.filter(created_by=request.user)
        UserFormCls = UserFormNonSU
        UserProfileFormCls = UserProfileFormNonSU

    if request.method == "GET":
        pwd_form = UserCreationForm()
        user_form = UserFormCls()
        userprofile_form = UserProfileFormCls()
        
    elif request.method == "POST":
        pwd_form = UserCreationForm(request.POST)
        user_form = UserFormCls(request.POST)
        userprofile_form = UserProfileFormCls(request.POST)
        if pwd_form.is_valid() and user_form.is_valid() and userprofile_form.is_valid():
            user = pwd_form.save()
            user_form = UserFormCls(request.POST, instance=user)
            user = user_form.save()
            up = UserProfile(user=user, created_by=request.user)
            userprofile_form = UserProfileFormCls(request.POST, instance=up)
            userprofile_form.save()
            return HttpResponseRedirect(reverse("user_saved", args=(user.id,)))
    else:
        return HttpResponseNotAllowed("GET", "POST")
    
    # Make sure they all have profiles
    for u in user_list:
        UserProfile.get_or_create_profile(u)
    
    return render_to_response('clearinghouse/user_list.html',
                              {'owner': request.user,
                               'user_list': user_list,
                               'pwd_form': pwd_form,
                               'user_form': user_form,
                               'userprofile_form': userprofile_form,
                               })

@user_passes_test(can_access)
def detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    profile = UserProfile.get_or_create_profile(user)
    if not request.user.is_staff and profile.created_by != request.user:
        return HttpResponseForbidden("You don't have sufficient rights to view or edit this user.")
    
    if request.user.is_staff:
        UserFormCls = UserFormSU
        UserProfileFormCls = UserProfileFormSU
    else:
        UserFormCls = UserFormNonSU
        UserProfileFormCls = UserProfileFormNonSU

    if request.method == "GET":
        pwd_form = AdminPasswordChangeFormDisabled(user)
        user_form = UserFormCls(instance=user)
        userprofile_form = UserProfileFormCls(instance=profile)
        
    elif request.method == "POST":
        pwd_form = AdminPasswordChangeFormDisabled(user, request.POST)
        user_form = UserFormCls(request.POST, instance=user)
        userprofile_form = UserProfileFormCls(request.POST, instance=profile)
        if user_form.is_valid() and userprofile_form.is_valid():
            user = user_form.save()
            userprofile_form = UserProfileFormCls(request.POST, instance=profile)
            userprofile_form.save()
            if "change_pwd" in request.POST and pwd_form.is_valid():
                pwd_form.save()
                return HttpResponseRedirect(reverse("user_saved", args=(user.id,)))
            elif "change_pwd" not in request.POST:
                return HttpResponseRedirect(reverse("user_saved", args=(user.id,)))
    else:
        return HttpResponseNotAllowed("GET", "POST")

    return render_to_response("clearinghouse/user_detail.html",
                              {'user': user,
                               'slices': user.slice_set.all(),
                               'pwd_form': pwd_form,
                               'user_form': user_form,
                               'show_owner': True,
                               'userprofile_form': userprofile_form,
                               })
    
@user_passes_test(can_access)
def saved(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    profile = UserProfile.get_or_create_profile(user)
    if not request.user.is_staff and profile.created_by != request.user:
        return HttpResponseForbidden("You don't have sufficient rights to view or edit this user.")
    
    return render_to_response("clearinghouse/user_saved.html",
                              {'user': user},
                              )

@user_passes_test(can_access)
def delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    profile = UserProfile.get_or_create_profile(user)
    if not request.user.is_staff and profile.created_by != request.user:
        return HttpResponseForbidden("You don't have sufficient rights to view or edit this user.")
    
    return create_update.delete_object(request,
                                       User,
                                       reverse("user_admin_home"),
                                       user_id,
                                       template_name="clearinghouse/user_confirm_delete.html")

