# Create your views here.
from openflow.optin_manager.settings import AUTO_APPROVAL_MODULES, SEND_EMAIL_WHEN_FLWOSPACE_APPROVED
from django.contrib.auth.decorators import login_required
from django.views.generic import simple
from django.db.models import Q
from openflow.optin_manager.users.models import UserProfile, Priority
from openflow.optin_manager.flowspace.models import FlowSpace
from openflow.optin_manager.opts.forms import AdminOptInForm
from openflow.optin_manager.flowspace.helper import copy_fs,\
    singlefs_is_subset_of, make_flowspace,multi_fs_intersect,  multifs_is_subset_of,\
    flowspaces_intersect_and_have_common_nonwildcard
from models import *
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from openflow.optin_manager.opts.models import UserFlowSpace, \
    AdminFlowSpace, UserOpts, OptsFlowSpace, MatchStruct
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
from openflow.optin_manager.admin_manager.forms import UserRegForm, ScriptProxyForm
from openflow.optin_manager.flowspace.utils import dotted_ip_to_int,\
mac_to_int
from django.forms.util import ErrorList
from openflow.optin_manager.opts.helper import update_user_opts
from helper import accept_user_fs_request, find_supervisor, convert_dict_to_flowspace,\
send_approve_or_reject_emial
from django.db import transaction
import logging

logger = logging.getLogger("SetAutoApproveScriptViews")

def promote_to_admin(request):
    profile = UserProfile.get_or_create_profile(request.user)
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
                    fv.proxy.api.changeFlowSpace(fv_args)    
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
                    fv.proxy.api.changeFlowSpace(fv_args)    
                    matches.delete()
                optfses.delete()
            opts.delete()
            
            # TODO: set all the supervisors
            
            #TODO: set all the approvers
            
            return HttpResponseRedirect("/dashboard")
    else:
            return simple.direct_to_template(request, 
                    template = "openflow/optin_manager/admin_manager/resign_admin.html",
                    extra_context = {
                                                 'user':request.user,
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
                fs = FlowSpace()
                fs.mac_src_s = mac_to_int(request.POST['mac_addr'])
                fs.mac_src_e = fs.mac_src_s
                fs.ip_src_s = dotted_ip_to_int(request.POST['ip_addr'])
                fs.ip_src_e = fs.ip_src_s
                fses.append(fs)
                fs = FlowSpace()
                fs.mac_dst_s = mac_to_int(request.POST['mac_addr'])
                fs.mac_dst_e = fs.mac_dst_s
                fs.ip_dst_s = dotted_ip_to_int(request.POST['ip_addr'])
                fs.ip_dst_e = fs.ip_dst_s
                fses.append(fs)
            elif (request.POST['mac_addr'] != "*"):
                fs = FlowSpace()
                fs.mac_src_s = mac_to_int(request.POST['mac_addr'])
                fs.mac_src_e = fs.mac_src_s
                fses.append(fs)
                fs = FlowSpace()
                fs.mac_dst_s = mac_to_int(request.POST['mac_addr'])
                fs.mac_dst_e = fs.mac_dst_s
                fses.append(fs)
            elif (request.POST['ip_addr'] != "0.0.0.0"):
                fs = FlowSpace()
                fs.ip_src_s = dotted_ip_to_int(request.POST['ip_addr'])
                fs.ip_src_e = fs.ip_src_s
                fses.append(fs)
                fs = FlowSpace()
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
            selected_admin = find_supervisor(fses)
            if (not selected_admin):
                raise Exception("No admin has full control over the requested flowspace")
            
            #check if any of the pending flowspace requests for this user is a subset of
            #this request. In this case, remove those old requests
            this_user_req_fs = RequestedUserFlowSpace.objects.filter(user=request.user)
            for fs in this_user_req_fs:
                if singlefs_is_subset_of(fs,fses):
                    fs.delete()
            
            # save the requested flowspace to database and commit it
            requested_fses = []
            for sfs in fses:
                rfs = RequestedUserFlowSpace(user=request.user,
                                          admin=selected_admin)
                copy_fs(sfs,rfs)
                rfs.save()
                requested_fses.append(rfs)
            transaction.commit()

                    
            # Now run the script specified by the admin for auto-approval
            script = AdminAutoApproveScript.objects.filter(admin=selected_admin)
            approved_fs = None
            if script.count() > 0:  #if Admin specified a script for auto-approval
                #create the request_info for approve function:
                request_info = {}
                if request.POST["mac_addr"] != "*":
                    request_info["req_mac_addr"] = request.POST["mac_addr"]
                if request.POST["ip_addr"] != "*":
                    request_info["req_ip_addr"] = request.POST["ip_addr"]
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
                    if (multifs_is_subset_of(to_be_saved,fses)):
                        
                        # step 3: add the approved fs to UserFlowSpace and update user opts
                        [fv_args,match_list] = accept_user_fs_request(to_be_saved)
                        try:
                            fv = FVServerProxy.objects.all()[0]
                            if len(fv_args) > 0:
                                returned_ids = fv.proxy.api.changeFlowSpace(fv_args)
                                for i in range(len(match_list)):
                                    match_list[i].fv_id = returned_ids[i]
                                    match_list[i].save()
                            for rfs in requested_fses:
                                rfs.delete()
                                
                            # send an e-mail if it is set in setting.SEND_EMAIL_WHEN_FLWOSPACE_APPROVED
                            if (SEND_EMAIL_WHEN_FLWOSPACE_APPROVED):
                                send_approve_or_reject_emial(to_be_saved,True)
                                
                            return simple.direct_to_template(request, 
                                template = "openflow/optin_manager/admin_manager/reg_request_successful.html",
                                extra_context = {'user':request.user,
                                                 'approved':True}
                            )  
                        except Exception,e:
                            import traceback
                            traceback.print_exc()
                            transaction.rollback()
                    else:
                        logger.debug("the function at %s approved a non-subset of original requested flowpssace"%import_path)

            if (approved_fs != None and len(approved_fs) == 0):
                return simple.direct_to_template(request,
                    template = "openflow/optin_manager/admin_manager/user_reg_fs.html",
                    extra_context = {
                        'error_msg':"Your flowspace request is automatically rejected by admin. Please try again.",
                        'form':form,
                                 },
                    )

            # if request needs manual approval
            return simple.direct_to_template(request, 
            template = "openflow/optin_manager/admin_manager/reg_request_successful.html",
                    extra_context = {'user':request.user,
                                     'approved':False,
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
                    send_approve_or_reject_emial([op_req],False)
                    op_req.delete() 
                       
    
    reqs = RequestedUserFlowSpace.objects.filter(admin=request.user).order_by('-user')
    flowspaces_intersect_and_have_common_nonwildcard
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

import re
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
         
   
def set_auto_approve(request):
    '''
    The view function for setting  user flowspace request auto approval script.
    request.POSt should have the following kye-value pairs:
    Key script: the script name
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
    
    
    
    