# Create your views here.
from django.contrib.auth.decorators import login_required
from django.views.generic import simple
from openflow.optin_manager.opts.models import AdminFlowSpace
from openflow.optin_manager.users.models import UserProfile, Priority
from openflow.optin_manager.opts.forms import AdminOptInForm
from openflow.optin_manager.flowspace.helper import \
    singlefs_is_subset_of, make_flowspace,multi_fs_intersect, copy_fs
from models import *
from django.http import HttpResponseRedirect
from openflow.optin_manager.opts.models import UserFlowSpace, \
    AdminFlowSpace, UserOpts, OptsFlowSpace, MatchStruct
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy


from django.forms.util import ErrorList

@login_required
def promote_to_admin(request):
    profile = request.user.get_profile()
    if (profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
 
    
    if (request.method == "POST"):
        form = AdminOptInForm(request.POST)
        if form.is_valid():
            optedFS = make_flowspace(request.POST)
            # check if the request FS is in strict hierarchy:
            # this means that for each of the available AdminFS
            # this should either be a subset of them or be disjoint
            # from them:
            admins_list = UserProfile.objects.filter(is_net_admin=True)
            intersected_admins = []
            intersected_supervisors = []
            for admin in admins_list:
                adminfs = AdminFlowSpace.objects.filter(user=admin.user)
                f = multi_fs_intersect(adminfs,[optedFS],FlowSpace)
                if (f):
                    if singlefs_is_subset_of(optedFS,adminfs):
                        intersected_admins.append(admin)
                        intersected_supervisors.append(admin.supervisor)
                    else:
                        msg = "The requested flowspace doesn't belong to a single \
                            admin"
                        form._errors["general"] = ErrorList([msg])
                        return simple.direct_to_template(request, 
                        template = "openflow/optin_manager/admin_manager/promote_to_admin.html",
                                extra_context = {
                                                 'form': form,
                                                 'user':request.user,
                                                 },
                            )
            selected_admin = None
            for admin in intersected_admins:
                if (admin not in intersected_supervisors or admin.supervisor==admin.user):
                    selected_admin = admin
                    break
            if (not selected_admin):
                #This shouldn't happen
                return 0
            
            suggested_prioirty = selected_admin.user.get_profile().\
                max_priority_level - Priority.Priority_Scale 
                
            save_fs = RequestedAdminFlowSpace.objects.filter(user=request.user)
            if not save_fs:
                save_fs = RequestedAdminFlowSpace(
                                                   user=request.user,
                                                   admin=selected_admin.user,
                                                   req_priority=suggested_prioirty)
            else:
                save_fs = save_fs[0]
                save_fs.admin = selected_admin.user
                save_fs.req_priority = suggested_prioirty

            copy_fs(optedFS,save_fs)
            save_fs.save()
            
            return simple.direct_to_template(request, 
            template ="openflow/optin_manager/admin_manager/admin_request_successful.html",
                                extra_context = {
                                                 'user':request.user,
                                                 },
                            )
            
    else:
        form = AdminOptInForm()
    return simple.direct_to_template(request, 
    template = "openflow/optin_manager/admin_manager/promote_to_admin.html",
                        extra_context = {
                                                 'form': form,
                                                 'user':request.user,
                                                 },
                        )
    
@login_required
def approve_admin(request,operation,req_id):
    profile = request.user.get_profile()
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    
    if (request.method == "POST"):
        op_req = RequestedAdminFlowSpace.objects.get(id=req_id)
        if (operation == 1):
            #update new admin profile
            op_profile = op_req.user.get_profile()
            op_profile.is_net_admin = True
            op_profile.supervisor = op_req.admin
            op_profile.max_priority_level = op_req.req_priority
            op_profile.save()
            
            # remove all the outstanding user flowspace requests
            RequestedUserFlowSpace.objects.filter(user=op_req.user).delete()
            
            # remove all the flowspaces belonging to this user
            UserFlowSpace.objects.filter(user=op_req.user).delete()
            
            # remove all user's optins as user
            fv = FVServerProxy.objects.all()[0]
            opts = UserOpts.objects.filter(user=op_req.user)
            for opt in opts:
                optfses = OptsFlowSpace.objects.filter(opt=opt)
                for optfs in optfses:
                    matches = MatchStruct.objects.filter(optfs=optfs)
                    fv_args = []
                    for match in matches:
                        fv_arg = {"operation":"REMOVE","id":match.fv_id}
                        fv_args.append(fv_arg)
                    fv.api.changeFlowSpace(fv_args)    
                    matches.delete()
                optfses.delete()
            opts.delete()
            
            #copy requested into AdminFlowSpace
            afs = AdminFlowSpace(user=op_req.user)
            copy_fs(op_req,afs)
            afs.save()
            
        op_req.delete()
    
            
    
    reqs = RequestedAdminFlowSpace.objects.filter(admin=request.user)
    return simple.direct_to_template(request, 
    template = "openflow/optin_manager/admin_manager/approve_admin.html",
                        extra_context = {
                                                 'reqs': reqs,
                                                 'user':request.user,
                                                 },
                        )   
    
@login_required
def resign_admin(request):
    profile = request.user.get_profile()
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    
    if (request.method == "POST"):
            op_profile = request.user.get_profile()
            op_profile.is_net_admin = False
            op_profile.save()
            
            # remove all the outstanding admin flowspace requests
            RequestedAdminFlowSpace.objects.filter(user=request.user).delete()
            
            # remove all the flowspaces belonging to this admin
            AdminFlowSpace.objects.filter(user=request.user).delete()
            
            # remove all admin's optins
            fv = FVServerProxy.objects.all()[0]
            opts = UserOpts.objects.filter(user=request.user)
            for opt in opts:
                optfses = OptsFlowSpace.objects.filter(opt=opt)
                for optfs in optfses:
                    matches = MatchStruct.objects.filter(optfs=optfs)
                    fv_args = []
                    for match in matches:
                        fv_arg = {"operation":"REMOVE","id":match.fv_id}
                        fv_args.append(fv_arg)
                    fv.api.changeFlowSpace(fv_args)    
                    matches.delete()
                optfses.delete()
            opts.delete()
            return HttpResponseRedirect("/dashboard")
    else:
            return simple.direct_to_template(request, 
                    template = "openflow/optin_manager/admin_manager/resign_admin.html",
                    extra_context = {
                                                 'user':request.user,
                                                 },
                    )     

    
@login_required
def user_add_fs(request):
    pass
    profile = request.user.get_profile()
    if (profile.is_net_admin):
        # TODO: send to correct page
        return 0
    
    if (request.method == "POST"):
        form = AdminOptInForm(request.POST)
        if form.is_valid():
            optedFS = make_flowspace(request.POST)
            # check if the request FS is in strict hierarchy:
            # this means that for each of the available AdminFS
            # this should either be a subset of them or be disjoint
            # from them:
            admins_list = UserProfile.objects.filter(is_net_admin=True)
            intersected_admins = []
            intersected_supervisors = []
            for admin in admins_list:
                adminfs = AdminFlowSpace.objects.filter(user=admin.user)
                f = multi_fs_intersect(adminfs,[optedFS],FlowSpace)
                if (f):
                    if singlefs_is_subset_of(optedFS,adminfs):
                        intersected_admins.append(admin)
                        intersected_supervisors.append(admin.supervisor)
                    else:
                        msg = "The requested flowspace doesn't belong to a single \
                            admin"
                        form._errors["general"] = ErrorList([msg])
                        return simple.direct_to_template(request, 
                        template = "openflow/optin_manager/admin_manager/promote_to_admin.html",
                                extra_context = {
                                                 'form': form,
                                                 'user':request.user,
                                                 },
                            )
            selected_admin = None
            for admin in intersected_admins:
                if (admin not in intersected_supervisors or admin.supervisor==admin.user):
                    selected_admin = admin
                    break
            if (not selected_admin):
                #This shouldn't happen
                return 0
            
            suggested_prioirty = selected_admin.user.get_profile().\
                max_priority_level - Priority.Priority_Scale 
                
            save_fs = RequestedAdminFlowSpace.objects.filter(user=request.user)
            if not save_fs:
                save_fs = RequestedAdminFlowSpace(
                                                   user=request.user,
                                                   admin=selected_admin.user,
                                                   req_priority=suggested_prioirty)
            else:
                save_fs = save_fs[0]
                save_fs.admin = selected_admin.user
                save_fs.req_priority = suggested_prioirty

            copy_fs(optedFS,save_fs)
            save_fs.save()
            
            return simple.direct_to_template(request, 
            template ="openflow/optin_manager/admin_manager/admin_request_successful.html",
                                extra_context = {
                                                 'user':request.user,
                                                 },
                            )
            
    else:
        form = AdminOptInForm()
    return simple.direct_to_template(request, 
    template = "openflow/optin_manager/admin_manager/promote_to_admin.html",
                        extra_context = {
                                                 'form': form,
                                                 'user':request.user,
                                                 },
                        )