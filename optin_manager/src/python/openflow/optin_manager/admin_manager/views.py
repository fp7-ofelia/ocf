# Create your views here.
from openflow.optin_manager.settings import AUTO_APPROVAL_MODULES, SEND_EMAIL_WHEN_FLWOSPACE_APPROVED
from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required
from django.views.generic import simple
from django.db.models import Q
from openflow.optin_manager.users.models import UserProfile, Priority
from openflow.optin_manager.flowspace.models import FlowSpace
from openflow.optin_manager.opts.forms import AdminOptInForm,UploadFileForm
from openflow.optin_manager.flowspace.helper import copy_fs,\
    singlefs_is_subset_of, single_fs_intersect, multifs_is_subset_of,\
    flowspaces_intersect_and_have_common_nonwildcard
from models import *
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from openflow.optin_manager.opts.models import UserFlowSpace, \
    AdminFlowSpace, UserOpts, OptsFlowSpace, MatchStruct
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
from openflow.optin_manager.admin_manager.forms import UserRegForm, ScriptProxyForm,\
    FlowSpaceAutoApproveScriptForm
from openflow.optin_manager.flowspace.utils import dotted_ip_to_int,\
mac_to_int, int_to_mac, int_to_dotted_ip
from django.forms.util import ErrorList
from openflow.optin_manager.opts.helper import update_user_opts, opt_fses_outof_exp,\
update_admin_opts, read_fs
from helper import accept_user_fs_request, find_supervisor, convert_dict_to_flowspace,\
send_approve_or_reject_email, update_fs_approver, send_admin_req_approve_or_reject_email
from django.db import transaction
import logging
import re
import os
import subprocess

logger = logging.getLogger("SetAutoApproveScriptViews")

def manage_user_fs(request):
    '''
    The view function to add/remove flowspaces for the users through an admin
    '''
    profile = UserProfile.get_or_create_profile(request.user)
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    
    all_users_tmp = UserProfile.objects.filter(is_net_admin=False)
    all_users = []
    for user in all_users_tmp:
        if user.is_clearinghouse_user and not profile.user.is_superuser:
            pass
        else:
            all_users.append(user)
            
    if len(all_users)==0:
        exist = False
        first_user = 0
    else:
        exist = True
        try:
            first_user = all_users[0].user.id
        except:
            first_user = 0
    
    return simple.direct_to_template(request, 
        template ="openflow/optin_manager/admin_manager/manage_user_fs.html",
            extra_context = {
                    'user':request.user,
                    'user_list':all_users,
                    'exist':exist,
                    'first_user':first_user,
            },
    )
    
    
def change_user_fs(request,user_id):
    profile = UserProfile.get_or_create_profile(request.user)
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    
    error_msg = []
    try:
        req_profile = UserProfile.objects.get(user__id=int(user_id))
    except:
        error_msg.append("Invalid user id")
        
    if len(error_msg)==0:
        if (req_profile.is_net_admin):
            error_msg.append("This user is an administrator")
            userfs = []
        else:
            if (request.method == "POST"):
                for key in request.POST:
                    deleting = re.match(r"del_(?P<id>\d+)",key)
    
                    try:
                        key_id = deleting.group("id")
                    except:
                        continue
                    
                    try:
                        fs_to_del = UserFlowSpace.objects.get(id=int(key_id))
                        if fs_to_del.approver == request.user:
                            fs_to_del.delete()
                        else:
                            error_msg.append("You don't have control over flowspace %s"%fs_to_del)
                    except:
                        error_msg.append("Invalid id(%s) found in the request.POST for user flowspace."%key_id)


                if "register_flowspace" in request.POST:
                    form = UserRegForm(request.POST)
                    if (form.is_valid()):
                        # Convert the request into an array of flowspace objects
                        added_fses = []
                        if (request.POST['mac_addr'] != "*" and request.POST['ip_addr'] != "0.0.0.0"):
                            fs = UserFlowSpace()
                            fs.mac_src_s = mac_to_int(request.POST['mac_addr'])
                            fs.mac_src_e = fs.mac_src_s
                            fs.ip_src_s = dotted_ip_to_int(request.POST['ip_addr'])
                            fs.ip_src_e = fs.ip_src_s
                            added_fses.append(fs)
                            fs = UserFlowSpace()
                            fs.mac_dst_s = mac_to_int(request.POST['mac_addr'])
                            fs.mac_dst_e = fs.mac_dst_s
                            fs.ip_dst_s = dotted_ip_to_int(request.POST['ip_addr'])
                            fs.ip_dst_e = fs.ip_dst_s
                            added_fses.append(fs)
                        elif (request.POST['mac_addr'] != "*"):
                            fs = UserFlowSpace()
                            fs.mac_src_s = mac_to_int(request.POST['mac_addr'])
                            fs.mac_src_e = fs.mac_src_s
                            added_fses.append(fs)
                            fs = UserFlowSpace()
                            fs.mac_dst_s = mac_to_int(request.POST['mac_addr'])
                            fs.mac_dst_e = fs.mac_dst_s
                            added_fses.append(fs)
                        elif (request.POST['ip_addr'] != "0.0.0.0"):
                            fs = UserFlowSpace()
                            fs.ip_src_s = dotted_ip_to_int(request.POST['ip_addr'])
                            fs.ip_src_e = fs.ip_src_s
                            added_fses.append(fs)
                            fs = UserFlowSpace()
                            fs.ip_dst_s = dotted_ip_to_int(request.POST['ip_addr'])
                            fs.ip_dst_e = fs.ip_dst_s
                            added_fses.append(fs)
                        else:
                            error_msg.append("You cannot request the entire flowspace!")
                        
                        if len(error_msg)==0:
                            #check if requested flowspace is a subset of this admin's flowspace:
                            sup_fs = AdminFlowSpace.objects.filter(user=request.user)
                            if not multifs_is_subset_of(added_fses,sup_fs):
                                error_msg.append("You don't own this flowspase to delegate to %s"%req_profile.user.username)
                                
                        if len(error_msg)==0:
                            prev_fs = UserFlowSpace.objects.filter(user=req_profile.user)
                            if multifs_is_subset_of(added_fses,prev_fs):
                                error_msg.append("This user already owns the flowspace or a superset of it.")
                            else:
                                prev_reqs = RequestedUserFlowSpace.objects.filter(user=req_profile.user)
                                # if there is a pending flowpsace request which is a subset of the new FS, delete that,
                                # and replace it with this new FS:
                                for preq in prev_reqs:
                                    if singlefs_is_subset_of(preq,added_fses):
                                        preq.delete()
                                        
                                # if there is a  flowpsace owned by this user which is a subset of the new FS, delete that,
                                # and replace it with this new FS:
                                for preq in prev_fs:
                                    if singlefs_is_subset_of(preq,added_fses):
                                        preq.delete()
    
                                for requested_fs in added_fses:
                                    requested_fs.user = req_profile.user
                                    requested_fs.approver = profile.user
                                    requested_fs.save()                        
                        
                else: # when 'register_flowspace is not checked
                    form = UserRegForm()
                    
                [fv_args, match_list] = update_user_opts(req_profile.user)
                try:
                    fv = FVServerProxy.objects.all()[0]
                    try:
                        if len(fv_args) > 0:
                            returned_ids = fv.proxy.api.changeFlowSpace(fv_args)
                        for i in range(len(match_list)):
                            match_list[i].fv_id = returned_ids[i]
                            match_list[i].save()
                    except Exception,e:
                        import traceback
                        traceback.print_exc()
                        transaction.rollback()
                        error_msg.append("Couldn't update user opts after updating the flowspace: %s"%str(e))
                except Exception,e:
                    import traceback
                    traceback.print_exc()
                    transaction.rollback()
                    error_msg.append("Flowvisor not set: %s"%str(e))

            else: # if not a POST request
                form = UserRegForm()
                
            userfs = UserFlowSpace.objects.filter(user=req_profile.user,approver=request.user)
    
    return simple.direct_to_template(request, 
        template ="openflow/optin_manager/admin_manager/change_user_fs.html",
            extra_context = {
                    'user_id':user_id,
                    'userfs': userfs,
                    'user':request.user,
                    'error_msg':error_msg,
                    'form':form,
            },
    )
    
    

def manage_admin_fs(request):
    '''
    The view function to add/remove flowspaces for the admins supervised by this admin
    '''
    profile = UserProfile.get_or_create_profile(request.user)
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    
    admins_supervised_by_me = UserProfile.objects.filter(Q(is_net_admin=True)
                                                      &  Q(supervisor=request.user)
                                                      & ~Q(user=request.user))
    if len(admins_supervised_by_me)==0:
        exist = False
        first_admin = 0
    else:
        exist = True
        first_admin = admins_supervised_by_me[0].user.id
        
    return simple.direct_to_template(request, 
        template ="openflow/optin_manager/admin_manager/manage_admin_fs.html",
            extra_context = {
                    'user':request.user,
                    'admin_list':admins_supervised_by_me,
                    'exist':exist,
                    'first_admin':first_admin,
            },
    )
    
def change_admin_fs(request,user_id):
    profile = UserProfile.get_or_create_profile(request.user)
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    
    error_msg = []
    try:
        req_profile = UserProfile.objects.get(user__id=int(user_id))
    except:
        error_msg.append("Invalid user id")
        
    if len(error_msg)==0:
        if (not req_profile.is_net_admin) or req_profile.supervisor != request.user or req_profile.user == request.user:
            error_msg.append("This user is not under your supervision")
            adminfs = []
        else:
            if (request.method == "POST"):
                for key in request.POST:
                    deleting = re.match(r"del_(?P<id>\d+)",key)
    
                    try:
                        key_id = deleting.group("id")
                    except:
                        continue
                    
                    try:
                        AdminFlowSpace.objects.get(id=int(key_id)).delete()
                    except:
                        error_msg.append("Invalid id(%s) found in the request.POST for admin flowspace."%key_id)


                if "register_flowspace" in request.POST:
                    # if this is a POST request and the checkbox for add flowspace
                    # is checked, add the flowspace for this user
                    form = AdminOptInForm(request.POST)
                    if form.is_valid():
                        requested_fs = form.get_flowspace(AdminFlowSpace)
                        sup_fs = AdminFlowSpace.objects.filter(user=request.user)
                        # verify that the requested flowspace is subset of the supervisor flowspace
                        if not singlefs_is_subset_of(requested_fs,sup_fs):
                            error_msg.append("You don't own this flowspace to delegate to admin %s"%req_profile.user.username)
                        else:
                            # check if the requested flowspace is a subset of a flowspace owned by this user,
                            # and if so, show an error msg
                            prev_fs = AdminFlowSpace.objects.filter(user=req_profile.user)
                            if singlefs_is_subset_of(requested_fs,prev_fs):
                                error_msg.append("This user already owns the flowspace or a superset of it.")
                            else:
                                prev_reqs = RequestedAdminFlowSpace.objects.filter(user=req_profile.user)
                                # if there is a pending flowpsace request which is a subset of this one, delete that,
                                # and replace it with this new FS:
                                for preq in prev_reqs:
                                    if singlefs_is_subset_of(preq,[requested_fs]):
                                        preq.delete()
                                        
                                # if there is a flowpsace owned by this admin which is a subset of this one, delete that,
                                # and replace it with this new FS:
                                for preq in prev_fs:
                                    if singlefs_is_subset_of(preq,[requested_fs]):
                                        preq.delete()

                                requested_fs.user = req_profile.user
                                requested_fs.save()

                else: # when 'register_flowspace is not checked
                    form = AdminOptInForm()
                    
                fv_args = update_admin_opts(req_profile.user)
                try:
                    fv = FVServerProxy.objects.all()[0]
                    try:
                        if len(fv_args) > 0:
                            fv.proxy.api.changeFlowSpace(fv_args)
                    except Exception,e:
                        import traceback
                        traceback.print_exc()
                        transaction.rollback()
                        error_msg.append("Couldn't update admin opts after deleting the flowspace: %s"%str(e))
                except Exception,e:
                    import traceback
                    traceback.print_exc()
                    transaction.rollback()
                    error_msg.append("Flowvisor not set: %s"%str(e))

            else: # if not a POST request
                form = AdminOptInForm()
                
            adminfs = AdminFlowSpace.objects.filter(user=req_profile.user)
    
    return simple.direct_to_template(request, 
        template ="openflow/optin_manager/admin_manager/change_admin_fs.html",
            extra_context = {
                    'user_id':user_id,
                    'adminfs': adminfs,
                    'user':request.user,
                    'error_msg':error_msg,
                    'form':form,
            },
    )
    
    

def promote_to_admin(request):
    '''
    The view function for promoting a user to network admin position
    '''
    profile = UserProfile.get_or_create_profile(request.user)
    if (profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    
    error_msg = []
    prev_reqs = AdminPromoteRequest.objects.filter(user=request.user)
    if (request.method == "POST"):
        try:
            text = request.POST["text"]
            req_admin = UserProfile.objects.get(user__id=int(request.POST["supervisor"]))
            req_position = request.POST["req_position"]
            prev_reqs.delete()
            AdminPromoteRequest.objects.create(user=request.user, admin=req_admin.user, text=text, requested_position=req_position)
            return simple.direct_to_template(request, 
                template ="openflow/optin_manager/admin_manager/admin_request_successful.html",
                extra_context = {
                    'user':request.user,
                },
            )
        except Exception,e:
            import traceback
            traceback.print_exc()
            transaction.rollback()
            error_msg.append("Invalid POST object keys")

    admins = UserProfile.objects.filter(is_net_admin=True)
    req_exist = False
    if prev_reqs.count()==1:
        req_exist = True
        req_admin = prev_reqs[0].admin
        text = prev_reqs[0].text
        req_position = prev_reqs[0].requested_position
    elif prev_reqs.count()==0:
        req_admin = admins[0]
        text = "Hi,\n\nI want to be network administrator in your department/building. Please approve my request.\n\nThanks,\n%s %s"%\
        (request.user.first_name,request.user.last_name)
        req_position = "e.g. X Building Admin"
    elif prev_reqs.count()>1:
        raise Exception("More than one AdminPromoteRequest for a user")
        

    return simple.direct_to_template(request, 
        template = "openflow/optin_manager/admin_manager/promote_to_admin.html",
        extra_context = {
            'req_exist':req_exist,
            'admins':admins,
            'text':text,
            'req_admin':req_admin,
            'req_position':req_position,
            'error_msg':error_msg,
        },
    )
    

def delete_promote_to_admin(request):
    '''
    To delete the 'promote to admin' request
    '''
    profile = UserProfile.get_or_create_profile(request.user)
    if (not profile.is_net_admin):
        AdminPromoteRequest.objects.filter(user=request.user).delete()
    return HttpResponseRedirect("/dashboard")
    

def admin_reg_fs(request):
    '''
    The view function for requesting fs for admin
    The request.POST contain the key-value pairs in AdminOptInForm
    '''
    profile = request.user.get_profile()
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
 
    # the first admin doesn't need to request fs. he/she already owns everything
    if profile.supervisor == profile.user:
        return HttpResponseRedirect("/dashboard")
 
    error_msg = []    
    sup_fs = AdminFlowSpace.objects.filter(user=profile.supervisor)
    if (request.method == "POST"):
        form = AdminOptInForm(request.POST)
        if form.is_valid():
            requested_fs = form.get_flowspace(RequestedAdminFlowSpace)
            # verify that the requested flowspace is subset of the supervisor flowspace
            if not singlefs_is_subset_of(requested_fs,sup_fs):
                error_msg.append("You can't request for this flowspace. Your flowspace request should be a subset of your supervisor flowspace")
            else:
                
                # check if the requested flowspace is a subset of previous flowspace request,
                # and if so, show an error message:
                prev_reqs = RequestedAdminFlowSpace.objects.filter(user=request.user)
                prev_fs = AdminFlowSpace.objects.filter(user=request.user)
                if singlefs_is_subset_of(requested_fs,prev_reqs):
                    error_msg.append("You already requested for this flowspace or a superset of it. You can delete the previous request, and then try again")
                elif singlefs_is_subset_of(requested_fs,prev_fs):
                    error_msg.append("You already own this flowspace or a superset of it. You can delete the flowspace that you own, and then try again")
                else:
                    # if there is a pending flowpsace request which is a subset of this one, delete that,
                    # and replace it with this new request:
                    for preq in prev_reqs:
                        if singlefs_is_subset_of(preq,[requested_fs]):
                            preq.delete()
                    # if there is a flowpsace owned by this admin which is a subset of this one, delete that,
                    # and replace it with this new request:
                    for preq in prev_fs:
                        if singlefs_is_subset_of(preq,[requested_fs]):
                            preq.delete()
                            
                    requested_fs.user = request.user
                    requested_fs.admin = profile.supervisor
                    requested_fs.req_priority = profile.max_priority_level
                    requested_fs.save()
                    return simple.direct_to_template(request, 
                    template ="openflow/optin_manager/admin_manager/admin_request_successful.html",
                        extra_context = {
                            'user':request.user,
                        },
                    )

    else:
        form = AdminOptInForm()
        
    uform = UploadFileForm()
    return simple.direct_to_template(request, 
        template = "openflow/optin_manager/admin_manager/admin_req_fs.html",
        extra_context = {
            'sup_fs':sup_fs,
            'form': form,
            'upload_form':uform,
            'user':request.user,
            'error_msg':error_msg,
        },
    )
    

def admin_reg_fs_by_file(request):
    '''
    The view function for requesting fs for admin
    The request.POST contain the key-value pairs in AdminOptInForm
    '''
    profile = request.user.get_profile()
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
 
    # the first admin doesn't need to request fs. he/she already owns everything
    if profile.supervisor == profile.user:
        return HttpResponseRedirect("/dashboard")
 
    error_msg = []    
    sup_fs = AdminFlowSpace.objects.filter(user=profile.supervisor)
    if (request.method == "POST"):
        uform = UploadFileForm(request.POST, request.FILES)
        if uform.is_valid():
            
            # parse the file and find the list of flowspaces to be requested
            result = read_fs(request.FILES['file'])
            
            # check if an error happened while parsing the file, 
            if len(result["error"])==0:
                if not multifs_is_subset_of(result['flowspace'],sup_fs):
                    error_msg.append("You can't request for this flowspace. Your flowspace request should be a subset of your supervisor flowspace")
                else:
            
            
                
                    # check if the requested flowspace is a subset of previous flowspace request,
                    # and if so, show an error message:
                    prev_reqs = RequestedAdminFlowSpace.objects.filter(user=request.user)
                    prev_fs = AdminFlowSpace.objects.filter(user=request.user)
                    
                    

                    if multifs_is_subset_of(result['flowspace'],prev_reqs):
                        error_msg.append("You already requested for this flowspace or a superset of it. You can delete the previous request, and then try again")
                    elif multifs_is_subset_of(result['flowspace'],prev_fs):
                        error_msg.append("You already own this flowspace or a superset of it. You can delete the flowspace that you own, and then try again")
                    else:
                        # if there is a pending flowpsace request which is a subset of this one, delete that,
                        # and replace it with this new request:
                        for preq in prev_reqs:
                            if singlefs_is_subset_of(preq,result['flowspace']):
                                preq.delete()
                        # if there is a flowpsace owned by this admin which is a subset of this one, delete that,
                        # and replace it with this new request:
                        for preq in prev_fs:
                            if singlefs_is_subset_of(preq,result['flowspace']):
                                preq.delete()
                      
                        for fs in result['flowspace']:
                            requested_fs = RequestedAdminFlowSpace()
                            copy_fs(fs,requested_fs)
                            requested_fs.user = request.user
                            requested_fs.admin = profile.supervisor
                            requested_fs.req_priority = profile.max_priority_level
                            requested_fs.save()
                            
                        return simple.direct_to_template(request, 
                        template ="openflow/optin_manager/admin_manager/admin_request_successful.html",
                            extra_context = {
                                'user':request.user,
                            },
                        )
            # if there is error while parsing the file
            else:
                error_msg = result["error"]

    else:
        uform = UploadFileForm()
        
    form = AdminOptInForm()
    return simple.direct_to_template(request, 
        template = "openflow/optin_manager/admin_manager/admin_req_fs.html",
        extra_context = {
            'sup_fs':sup_fs,
            'form': form,
            'upload_form':uform,
            'user':request.user,
            'error_msg':error_msg,
        },
    )


def approve_admin(request):
    '''
    The view function for approving an admin flowspace request.
    the request.POST should have req_<RequestedAdminFlowSpace database id> as the
    key, and one of the accpet/reject/none as the decision taken for that flowspace
    request.
    '''
    profile = request.user.get_profile()
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    
    error_msg = []
    if (request.method == "POST"):
        
        keys = request.POST.keys()
        fv_args = []
        accepted_fs_reqs = []
        accepted_adm_reqs = []
        rejected_fs_reqs = []
        rejected_adm_reqs = []
        for key in keys:
            if key.startswith("adm_req_"):
                try:
                    req_id = int(key[8:len(key)])
                    op_req = AdminPromoteRequest.objects.get(id=req_id)
                except Exception,e:
                    error_msg.append("%s is not a vlid request id!"%key)
                    continue
                
                decision = request.POST[key]
                op_profile = op_req.user.get_profile()
                if (decision=="accept"):
                    op_profile.is_net_admin = True
                    op_profile.supervisor = op_req.admin
                    op_profile.max_priority_level = \
                        op_req.admin.get_profile().max_priority_level - Priority.Priority_Margin
                    op_profile.admin_position = op_req.requested_position
                    op_profile.save()

                    # remove all the flowspaces belonging to this user
                    UserFlowSpace.objects.filter(user=op_req.user).delete()
                    
                    # remove all the user opts for this user
                    opts = UserOpts.objects.filter(user=op_req.user)
                        
                    for opt in opts:
                        optfses = OptsFlowSpace.objects.filter(opt=opt)
                        new_fv_args = opt_fses_outof_exp(optfses)
                        fv_args = fv_args + new_fv_args
                        
                    adm_tmp = AdminPromoteRequest(user=op_req.user,admin=op_req.admin,
                                text=op_req.text, requested_position=op_req.requested_position)
                    accepted_adm_reqs.append(adm_tmp)
                    op_req.delete()
                    opts.delete()
                    
                if (decision=="reject"):
                    adm_tmp = AdminPromoteRequest(user=op_req.user,admin=op_req.admin,
                                text=op_req.text, requested_position=op_req.requested_position)
                    op_req.delete()
                    rejected_adm_reqs.append(adm_tmp)
                    
            elif key.startswith("fs_req_"):
                try:
                    req_id = int(key[7:len(key)])
                    op_req = RequestedAdminFlowSpace.objects.get(id=req_id)
                except Exception,e:
                    error_msg.append("%s is not a vlid request id!"%key)
                    continue
                
                decision = request.POST[key]
                if (decision=="accept"):
                    afs = AdminFlowSpace(user=op_req.user)
                    copy_fs(op_req,afs)
                    afs.save()
                    accepted_fs_reqs.append(afs)
                    op_req.delete()
            
                if (decision=="reject"):
                    temp = RequestedAdminFlowSpace(admin=op_req.admin, user=op_req.user)
                    copy_fs(op_req,temp)
                    rejected_fs_reqs.append(temp)
                    op_req.delete()

        
        # update the flowspace approvers for all the potentially affected flowspaces
        update_fs_approver(request.user)
        
        # Opt out all the opt-ins as user
        fv_success = True
        try:
            if len(fv_args) > 0:
                fv = FVServerProxy.objects.all()[0]
                fv.proxy.api.changeFlowSpace(fv_args)
        except Exception,e:
            import traceback
            traceback.print_exc()
            transaction.rollback()
            error_msg.append("Couldn't opt out the user before promoting to admin: %s"%str(e))
            fv_success = False

            if fv_success:
                # send out e-mails about decisions
                for req in rejected_adm_reqs:
                    send_admin_req_approve_or_reject_email(req,False)
                for req in accepted_adm_reqs:
                    send_admin_req_approve_or_reject_email(req,True)
                for req in rejected_fs_reqs:
                    send_approve_or_reject_email(req,False)
                for req in accepted_fs_reqs:
                    send_approve_or_reject_email(req,True)
    
    reqs = RequestedAdminFlowSpace.objects.filter(admin=request.user).order_by('-user')
    reqs_and_conflicts = []
    for req in reqs:
        new_conflicts = []
        all_admin_fs = AdminFlowSpace.objects.filter(~Q(user=req.user))
        all_admin_fs_req = RequestedAdminFlowSpace.objects.filter(~Q(user=req.user) & Q(admin=request.user))
        for fs in all_admin_fs:
            if flowspaces_intersect_and_have_common_nonwildcard(req,fs):
                user_supervisor = fs.user.get_profile().supervisor
                new_conflicts.append("Conflict with %s %s (username: %s)'s flowspace approved by %s %s (username: %s): %s "%
                        (fs.user.first_name,fs.user.last_name,fs.user.username,
                         user_supervisor.first_name, user_supervisor.last_name, user_supervisor.username,fs)
                    )
        for fs in all_admin_fs_req:
            if flowspaces_intersect_and_have_common_nonwildcard(req,fs):
                new_conflicts.append("Conflict with %s %s (username: %s)'s pending flowspace request: %s "%
                        (fs.user.first_name,fs.user.last_name,fs.user.username,fs)
                    )
        if len(new_conflicts) > 0:
            reqs_and_conflicts.append({"req":req,"conflicts":new_conflicts})
        else:
            reqs_and_conflicts.append({"req":req,"conflicts":0})

    new_admin_reqs = AdminPromoteRequest.objects.filter(admin=request.user)
    return simple.direct_to_template(request, 
        template = "openflow/optin_manager/admin_manager/approve_admin.html",
        extra_context = {
                'error_msg':error_msg,
                'fs_reqs': reqs_and_conflicts,
                'admin_reqs':new_admin_reqs,
                'user':request.user,
        },
    )   
    

def resign_admin(request):
    '''
    View function for an admin to resign from admin position
    '''
    profile = request.user.get_profile()
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    
    # the first admin doesn't need to request fs. he/she already owns everything
    if profile.supervisor == profile.user:
        return HttpResponseRedirect("/dashboard")
    
    error_msg = []
    if (request.method == "POST"):
        profile.is_net_admin = False
        profile.save()
            
        # remove all the outstanding admin flowspace requests
        RequestedAdminFlowSpace.objects.filter(user=request.user).delete()
            
        # remove all the flowspaces belonging to this admin
        AdminFlowSpace.objects.filter(user=request.user).delete()
            
        # remove all admin's optins
        opts = UserOpts.objects.filter(user=request.user)
        fv_args = []
        for opt in opts:
            optfses = OptsFlowSpace.objects.filter(opt=opt)
            fv_args = opt_fses_outof_exp(optfses)
        opts.delete()
            
        # update the supervisor of all admins supervised by this this admin
        # to this admin's supervisor
        this_admin_supervisor = profile.supervisor
        admins_list = UserProfile.objects.filter(is_net_admin=True,supervisor=request.user)
            
        for admin in admins_list:
            admin.supervisor = this_admin_supervisor
            admin.save()
                
        # update the approver/admin for all userflowspace objects and userflowspacerequest objects
        update_fs_approver(request.user)
            
        try:
            if len(fv_args) > 0:
                fv = FVServerProxy.objects.all()[0]
                fv.proxy.api.changeFlowSpace(fv_args)
            return HttpResponseRedirect("/dashboard")
        except Exception,e:
            import traceback
            traceback.print_exc()
            transaction.rollback()
            error_msg.append("Couldn't call flowvisor to update flowspaces: %s"%str(e))
                
            
            

    return simple.direct_to_template(request, 
        template = "openflow/optin_manager/admin_manager/resign_admin.html",
        extra_context = {
            'user':request.user,
            'error_msg':error_msg,
        },
    )     


def user_reg_fs(request):
    '''
    The view function to send a flowspace request for admin. 
    1) Checks if the user already have the requested flowspace or have a pending
    request for it, and if this is not the case, requests that flowspace
    2) Then finds out which admin has complete control over the flowspace to approve it
    3) Then runs an optional script for approving the request. this script is either
    a local script in the openflow.optin_manager.auto_approve_scripts or is a custom, remote
    script that is called using XMLRPC call.
    In either case 
    4) If the optional script doesn't exist or if it postpones the result, a request will
    be sent to the admin.
    
    request.POST has the following key-value pairs:
    @param ip_addr: requested IP address for the flowspace in the format of x.x.x.x
    @type ip_addr: string
    @param mac_addr: request MAC address for the flowspace in the format of xx:xx:xx:xx:xx:xx
    @type mac_addr: string 
    '''
    profile = UserProfile.get_or_create_profile(request.user)
    
    #admins can not see this page. redirect them to dashboard
    if (profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    
    if (request.method == "POST"):
        form = UserRegForm(request.POST)
        if (form.is_valid()):

            # Convert the request into an array of flowspace objects
            fses = []
            if (request.POST['mac_addr'] != "*" and request.POST['ip_addr'] != "0.0.0.0"):
                fs = RequestedUserFlowSpace()
                fs.mac_src_s = mac_to_int(request.POST['mac_addr'])
                fs.mac_src_e = fs.mac_src_s
                fs.ip_src_s = dotted_ip_to_int(request.POST['ip_addr'])
                fs.ip_src_e = fs.ip_src_s
                fses.append(fs)
                fs = RequestedUserFlowSpace()
                fs.mac_dst_s = mac_to_int(request.POST['mac_addr'])
                fs.mac_dst_e = fs.mac_dst_s
                fs.ip_dst_s = dotted_ip_to_int(request.POST['ip_addr'])
                fs.ip_dst_e = fs.ip_dst_s
                fses.append(fs)
            elif (request.POST['mac_addr'] != "*"):
                fs = RequestedUserFlowSpace()
                fs.mac_src_s = mac_to_int(request.POST['mac_addr'])
                fs.mac_src_e = fs.mac_src_s
                fses.append(fs)
                fs = RequestedUserFlowSpace()
                fs.mac_dst_s = mac_to_int(request.POST['mac_addr'])
                fs.mac_dst_e = fs.mac_dst_s
                fses.append(fs)
            elif (request.POST['ip_addr'] != "0.0.0.0"):
                fs = RequestedUserFlowSpace()
                fs.ip_src_s = dotted_ip_to_int(request.POST['ip_addr'])
                fs.ip_src_e = fs.ip_src_s
                fses.append(fs)
                fs = RequestedUserFlowSpace()
                fs.ip_dst_s = dotted_ip_to_int(request.POST['ip_addr'])
                fs.ip_dst_e = fs.ip_dst_s
                fses.append(fs)
            else:
                return simple.direct_to_template(request,
                    template = "openflow/optin_manager/admin_manager/user_reg_fs.html",
                    extra_context = {
                        'error_msg':"Can not request the entire flowspace!",
                        'form':form,
                                 },
                    )
                
            # check if the requested flowspace is not already requested or owned by this user:
            user_fs = UserFlowSpace.objects.filter(user=request.user)
            req_fs = RequestedUserFlowSpace.objects.filter(user=request.user)
            owned_and_requested = []
            for fs in user_fs:
                owned_and_requested.append(fs)
            for fs in req_fs:
                owned_and_requested.append(fs)
            updated_fses = []
            for fs in fses:
                is_subset = singlefs_is_subset_of(fs,owned_and_requested)
                if (not is_subset):
                    updated_fses.append(fs)
            if len(updated_fses)==0:
                return simple.direct_to_template(request,
                    template = "openflow/optin_manager/admin_manager/user_reg_fs.html",
                    extra_context = {
                        'error_msg':"You have either already owned this flowspace or have a pending request for it",
                        'form':form,
                                 },
                    )
            else:
                fses = updated_fses
                    
            # Now find out the admin who has the right to approve the request
            selected_admins = []
            for fs in fses:
                selected_admin = find_supervisor([fs])
                if (not selected_admin):
                    raise Exception("No admin has full control over the requested flowspace")
                selected_admins.append(selected_admin)
            
            #check if any of the pending flowspace requests for this user is a subset of
            #this request. In this case, remove those old requests
            this_user_req_fs = RequestedUserFlowSpace.objects.filter(user=request.user)
            for fs in this_user_req_fs:
                if singlefs_is_subset_of(fs,fses):
                    fs.delete()
                    
            # Now run the script specified by the admin for auto-approval
            approved_msg = []
            rejected_msg = []
            awaiting_msg = []
            fv_args = []
            match_list = []
            for i in range(len(fses)):
                selected_admin = selected_admins[i]
                fses[i].admin = selected_admin
                fses[i].user = request.user
                script = AdminAutoApproveScript.objects.filter(admin=selected_admin)
                approved_fs = None
                if script.count() > 0:  #if Admin specified a script for auto-approval
                    #create the request_info for approve function:
                    request_info = {}
                    if fses[i].mac_src_s == fses[i].mac_src_e:
                        request_info["req_mac_addr_src"] = int_to_mac(fses[i].mac_src_s)
                    if fses[i].mac_dst_s == fses[i].mac_dst_e:
                        request_info["req_mac_addr_dst"] = int_to_mac(fses[i].mac_dst_s)
                    if fses[i].ip_src_s == fses[i].ip_src_e:
                        request_info["req_ip_addr_src"] = int_to_dotted_ip(fses[i].ip_src_s)
                    if fses[i].ip_dst_s == fses[i].ip_dst_e:
                        request_info["req_ip_addr_dst"] = int_to_dotted_ip(fses[i].ip_dst_s)
                    if  "REMOTE_ADDR" in request.META:
                        request_info["remote_addr"] = request.META['REMOTE_ADDR']
                    request_info["user_last_name"] = request.user.last_name
                    request_info["user_first_name"] = request.user.first_name
                    request_info["user_email"] = request.user.email
                    
                    # run the local or remote auto-approve function
                    if (not script[0].remote) and (script[0].script_name in AUTO_APPROVAL_MODULES.keys()): 
                        #user uses system auto-approve functions
                        script_name = AUTO_APPROVAL_MODULES[script[0].script_name]
                        import_path = "openflow.optin_manager.auto_approval_scripts.%s"%(script_name)
                        try:
                            _temp = __import__(import_path,globals(), locals(),['approve'])
                            approve = _temp.approve
                            approved_fs = approve(request_info)
                        except:
                            import traceback
                            traceback.print_exc()
                            pass
                    elif script[0].remote:
                        try:
                            proxy = AutoApproveServerProxy.objects.get(admin=selected_admin)
                            approved_fs = proxy.approve(request_info)
                        except:
                            import traceback
                            traceback.print_exc()
                            pass
                    
                    # if auto-approve script has approved something:
                    # 1) convert the approved flowspace to a list of FlowSpace objects
                    # 2) check if the approved flowpsace is a subset of request
                    # 3) add the approved fs to UserFlowSpace and update user opts
                    if (approved_fs != None and len(approved_fs) > 0):
                        #step 1:convert the approved flowspace to a list of RequestedUserFlowSpace objects
                        to_be_saved = convert_dict_to_flowspace(approved_fs,RequestedUserFlowSpace)
                        for fs in to_be_saved:
                            fs.admin = selected_admin
                            fs.user = request.user
                            fs.save()
                        
                        # step 2: check if the approved flowpsace is a subset of request
                        if (multifs_is_subset_of(to_be_saved,[fses[i]])):
                            # step 3: add the approved fs to UserFlowSpace and update user opts
                            [new_fv_args,new_match_list] = accept_user_fs_request(to_be_saved)
                            fv_args = fv_args + new_fv_args
                            match_list = match_list + new_match_list
                            for fs in to_be_saved:
                                appr = RequestedUserFlowSpace()
                                appr.admin = fs.admin
                                appr.user = fs.user
                                copy_fs(fs,appr)
                                approved_msg.append(appr)

                        else:
                            awaiting_msg.append("Flowspace '%s' is awaiting admin approval"%fses[i])
                            logger.debug("the function at %s approved a non-subset of original requested flowpssace"%import_path)
                    
                    # If autoa-aprove script rejected the request
                    if (approved_fs != None and len(approved_fs) == 0):
                        rejected_msg.append(fses[i])
                        
                # flowspaces awaiting manual decision
                if approved_fs == None:
                    rfs = RequestedUserFlowSpace(user=request.user,admin=selected_admin)
                    copy_fs(fses[i],rfs)
                    rfs.save()
                    awaiting_msg.append(fses[i])

            # Now, outside of for loop on fses, update flowvisor entries: 
            try:
                if len(fv_args) > 0:
                    fv = FVServerProxy.objects.all()[0]
                    returned_ids = fv.proxy.api.changeFlowSpace(fv_args)
                    for i in range(len(match_list)):
                        match_list[i].fv_id = returned_ids[i]
                        match_list[i].save()    

            except Exception,e:
                import traceback
                traceback.print_exc()
                transaction.rollback()
                return simple.direct_to_template(request,
                    template = "openflow/optin_manager/admin_manager/user_reg_fs.html",
                    extra_context = {
                        'error_msg':"Error when trying to update flowvisor: %s"%e,
                        'form':form,
                    },
                )
                
            # send an e-mail confirming the approved flowspaces for user.
            # (if it is set in setting.SEND_EMAIL_WHEN_FLWOSPACE_APPROVED)
            if (SEND_EMAIL_WHEN_FLWOSPACE_APPROVED and len(approved_msg)>0):
                send_approve_or_reject_email(approved_msg,True)


            return simple.direct_to_template(request, 
            template = "openflow/optin_manager/admin_manager/reg_request_successful.html",
                    extra_context = {'user':request.user,
                                     'approved_msg':approved_msg,
                                     'rejected_msg':rejected_msg,
                                     'awaiting_msg':awaiting_msg,
                                     }
            )           

    else: #not a POST request
        form_input = {}
        if "REMOTE_ADDR" in request.META:
            form_input['ip_addr'] = request.META['REMOTE_ADDR']
        else:
            form_input['ip_addr'] = "0.0.0.0"
        form_input['mac_addr'] = "*"
        form = UserRegForm(form_input)
        
    return simple.direct_to_template(request,
                template = "openflow/optin_manager/admin_manager/user_reg_fs.html",
                extra_context = {
                        'error_msg':"",
                        'form':form,
                                 },
        )



def approve_user(request):
    '''
    The view function for manually approving a user flowspace request.
    When preparing data for the templates, it also finds out all the flowspaces
    (either pending or approved) that have a conflict with each of the flowspace 
    requests, and generate a warning for the admin.
    the key-value pairs in request is 
    @key: req_<request database id>
    @value: accept/reject/decline
    '''
    profile = request.user.get_profile()
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    
    error_msg = []
    if (request.method == "POST"):
        
        keys = request.POST.keys()
        for key in keys:
            if key.startswith("req_"):
                try:
                    req_id = int(key[4:len(key)])
                    op_req = RequestedUserFlowSpace.objects.get(id=req_id)
                except Exception,e:
                    error_msg.append("%s is not a vlid request id!"%key)
                
                decision = request.POST[key]
                if (decision=="accept"):
                    op_profile = op_req.user.get_profile()
                    op_profile.max_priority_level = Priority.Strict_User
                    op_profile.save()
            
                    [fv_args, match_list] = accept_user_fs_request([op_req])
                    try:
                        fv = FVServerProxy.objects.all()[0]
                        if len(fv_args) > 0:
                            returned_ids = fv.proxy.api.changeFlowSpace(fv_args)
                            for i in range(len(match_list)):
                                match_list[i].fv_id = returned_ids[i]
                                match_list[i].save()

                    except Exception,e:
                        import traceback
                        traceback.print_exc()
                        transaction.rollback()
                    
            
                elif (decision=="reject"):
                    send_approve_or_reject_email([op_req],False)
                    op_req.delete() 
                       
    
    reqs = RequestedUserFlowSpace.objects.filter(admin=request.user).order_by('-user')
    # find all the conflicts between reqs themselves and between them and already 
    # approved flowspaces
        
    reqs_and_conflicts = []
    for req in reqs:
        new_conflicts = []
        all_user_fs = UserFlowSpace.objects.filter(~Q(user=req.user))
        all_user_fs_req = RequestedUserFlowSpace.objects.filter(~Q(user=req.user) & Q(admin=request.user))
        for fs in all_user_fs:
            if flowspaces_intersect_and_have_common_nonwildcard(req,fs):
                new_conflicts.append("Conflict with %s %s (username: %s)'s flowspace approved by %s %s (username: %s): %s "%
                        (fs.user.first_name,fs.user.last_name,fs.user.username,
                         fs.approver.first_name, fs.approver.last_name, fs.approver.username,fs)
                    )
        for fs in all_user_fs_req:
            if flowspaces_intersect_and_have_common_nonwildcard(req,fs):
                new_conflicts.append("Conflict with %s %s (username: %s)'s pending flowspace request: %s "%
                        (fs.user.first_name,fs.user.last_name,fs.user.username,fs)
                    )
                
        if len(new_conflicts) > 0:
            reqs_and_conflicts.append({"req":req,"conflicts":new_conflicts})
        else:
            reqs_and_conflicts.append({"req":req,"conflicts":0})
        
    return simple.direct_to_template(request, 
            template = "openflow/optin_manager/admin_manager/approve_user.html",
            extra_context = {
                        'reqs': reqs_and_conflicts,
                        'user':request.user,
                        'error_msg':error_msg,
                    },
        )  


def user_unreg_fs(request):
    '''
    The view function for unregistering  user flowspaces or pending flowspace requests
    the request.POSt is a dictionary with keys being either pend_<RequestedUserFlowSpace.id>
    or verif_<UserFlowSpace.id> and "checked" as the corresponding values.
    '''
    profile = UserProfile.get_or_create_profile(request.user)
    if (profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    
    error_msg = []
    if (request.method == "POST"):
        fs_changed = False
        for key in request.POST:
            verified = re.match(r"verif_(?P<id>\d+)",key)
            pending = re.match(r"pend_(?P<id>\d+)",key)
            try:
                status = 0
                if (verified):
                    key_id = verified.group("id")
                    status = 1
                elif (pending):
                    key_id =pending.group("id")
                    status = 2
            except:
                continue
            if (status == 1):
                fs_changed = True
                try:
                    UserFlowSpace.objects.get(id=int(key_id)).delete()
                except:
                    error_msg.append("Invalid id(%s) found in the request.POST for user flowspace."%key_id)
            elif (status == 2):
                try:
                    RequestedUserFlowSpace.objects.get(id=int(key_id)).delete()
                except:
                    error_msg.append("Invalid id(%s) found in the request.POST for user pending flowspace."%key_id)

        if fs_changed:
            [fv_args, match_list] = update_user_opts(request.user)
            try:
                fv = FVServerProxy.objects.all()[0]
                try:
                    if len(fv_args) > 0:
                        returned_ids = fv.proxy.api.changeFlowSpace(fv_args)
                    for i in range(len(match_list)):
                        match_list[i].fv_id = returned_ids[i]
                        match_list[i].save()
                except Exception,e:
                    import traceback
                    traceback.print_exc()
                    transaction.rollback()
                    error_msg.append("Couldn't update user opts after deleting the flowspace: %s"%str(e))
            except Exception,e:
                import traceback
                traceback.print_exc()
                transaction.rollback()
                error_msg.append("Flowvisor not set: %s"%str(e))
            
        
            
    userfs = UserFlowSpace.objects.filter(user=request.user)
    reqfs = RequestedUserFlowSpace.objects.filter(user=request.user)
    return simple.direct_to_template(request, 
            template = "openflow/optin_manager/admin_manager/user_unreg_fs.html",
            extra_context = {
                    'reqfs': reqfs,
                    'userfs': userfs,
                    'user':request.user,
                    'error_msg':error_msg,
               },
        )   
    
def admin_unreg_fs(request):
    '''
    The view function for unregistering  admin flowspaces or pending flowspace requests
    the request.POSt is a dictionary with keys being either pend_<RequestedAdminFlowSpace.id>
    or verif_<AdminFlowSpace.id> and "checked" as the corresponding values.
    '''
    profile = UserProfile.get_or_create_profile(request.user)
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    
    # the first admin can't give up the "all" flowspace he/she owns
    if profile.supervisor == profile.user:
        return HttpResponseRedirect("/dashboard")
    
    error_msg = []
    if (request.method == "POST"):
        fs_changed = False
        for key in request.POST:
            verified = re.match(r"verif_(?P<id>\d+)",key)
            pending = re.match(r"pend_(?P<id>\d+)",key)
            try:
                status = 0
                if (verified):
                    key_id = verified.group("id")
                    status = 1
                elif (pending):
                    key_id =pending.group("id")
                    status = 2
            except:
                continue
            if (status == 1):
                fs_changed = True
                try:
                    AdminFlowSpace.objects.get(id=int(key_id)).delete()
                except:
                    error_msg.append("Invalid id(%s) found in the request.POST for admin flowspace."%key_id)
            elif (status == 2):
                try:
                    RequestedAdminFlowSpace.objects.get(id=int(key_id)).delete()
                except:
                    error_msg.append("Invalid id(%s) found in the request.POST for admin pending flowspace."%key_id)

        if fs_changed:
            fv_args = update_admin_opts(request.user)
            try:
                fv = FVServerProxy.objects.all()[0]
                try:
                    if len(fv_args) > 0:
                        fv.proxy.api.changeFlowSpace(fv_args)
                except Exception,e:
                    import traceback
                    traceback.print_exc()
                    transaction.rollback()
                    error_msg.append("Couldn't update admin opts after deleting the flowspace: %s"%str(e))
            except Exception,e:
                import traceback
                traceback.print_exc()
                transaction.rollback()
                error_msg.append("Flowvisor not set: %s"%str(e))
            
    adminfs = AdminFlowSpace.objects.filter(user=request.user)
    reqfs = RequestedAdminFlowSpace.objects.filter(user=request.user)
    return simple.direct_to_template(request, 
            template = "openflow/optin_manager/admin_manager/admin_unreg_fs.html",
            extra_context = {
                    'reqfs': reqfs,
                    'adminfs': adminfs,
                    'user':request.user,
                    'error_msg':error_msg,
               },
        )
         
   
def set_auto_approve_original(request):
    '''
    The view function for setting  user flowspace request auto approval script.
    request.POSt should have the following kye-value pairs:
    @key script: @value: the script name
    if script name is Remote, it should have all the PasswordXMLRPCServerProxy keys. 
    '''
    profile = UserProfile.get_or_create_profile(request.user)
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")
    
    script_proxies = AutoApproveServerProxy.objects.filter(admin=request.user)
    if len(script_proxies)>0:
        script_proxy = script_proxies[0]
    else:
        script_proxy = AutoApproveServerProxy.objects.create(admin=request.user)
    
    script = AdminAutoApproveScript.objects.get_or_create(admin=request.user)[0]

    # prepare a list of script options to be set
    user_script_options = ["Manual"]
    user_script_options = user_script_options + AUTO_APPROVAL_MODULES.keys()
    user_script_options.append("Remote")
    
    error_msg = []
    if (request.method == "POST"):
        if request.POST["script"] not in user_script_options:
            error_msg.append("Invalid script name %s"%request.POST["script"])
        elif request.POST["script"] == "Remote":
            form = ScriptProxyForm(request.POST,instance=script_proxy)
            if form.is_valid():
                script.remote = True
                script.script_name = request.POST["script"]
                logger.debug("Form is valid")
                script_proxy = form.save()
                script.save()
                return HttpResponseRedirect(reverse("dashboard"))

        else:
            form = ScriptProxyForm(instance=script_proxy)
            script.remote = False
            script.script_name = request.POST["script"]
            script.save()
            return HttpResponseRedirect(reverse("dashboard"))
        
    else:
        form = ScriptProxyForm(instance=script_proxy)
    

    return simple.direct_to_template(request, 
            template = "openflow/optin_manager/admin_manager/set_auto_approve.html",
            extra_context = {
                    'user_script_options':user_script_options,
                    'error_msg':error_msg,
                    'form':form,
                    'current_script':script.script_name,
               },
        )

def set_auto_approve(request):
    """
    Set automatic grant of VLANs and approval of Flowspaces
    """
    profile = UserProfile.get_or_create_profile(request.user)
    if (not profile.is_net_admin):
        return HttpResponseRedirect("/dashboard")

    script_proxies = FlowSpaceAutoApproveScript.objects.filter(admin=request.user)
    if len(script_proxies)>0:
        script_proxy = script_proxies[0]
    else:
        script_proxy = FlowSpaceAutoApproveScript.objects.create(admin=request.user)

    # prepare a list of script options to be set
    user_script_options = ["Manual"] + AUTO_APPROVAL_MODULES.keys()
    error_msg = []

    if (request.method == "POST"):
        if request.POST["script"] not in user_script_options:
            error_msg.append("Invalid script name %s" % request.POST["script"])
        else:
            redirect_to_main = False
            form = FlowSpaceAutoApproveScriptForm(request.POST,instance=script_proxy)
            if form.is_valid():
                # If no checkbox selected in Automatic, swich to "Manual"
                if not script_proxy.vlan_auto_grant and not script_proxy.flowspace_auto_approval:
                    error_msg.append("No automatic option selected")
                    script_proxy.script_name = "Manual"
                # Otherwise move on
                else:
                    redirect_to_main = True
                    script_proxy.script_name = request.POST["script"]
                script_proxy = form.save()
                script_proxy.save()
            else:
                error_msg.append(form.errors["__all__"])
                # If no Flowspace automatic approval checkbox selected in Automatic, skip to "Manual"
                if script_proxy.script_name != "Manual" and form.data["script"] != "Manual":
                    script_proxy.script_name = "Manual"
                    script_proxy.save()
        if redirect_to_main:
            return HttpResponseRedirect(reverse("dashboard"))
    else:
        form = FlowSpaceAutoApproveScriptForm(instance=script_proxy)
    
    return simple.direct_to_template(request,
            template = "openflow/optin_manager/admin_manager/set_auto_approve.html",
            extra_context = {
                    'user_script_options': user_script_options,
                    'error_msg': error_msg,
                    'form': form,
                    'current_script': script_proxy.script_name,
               },
        )

