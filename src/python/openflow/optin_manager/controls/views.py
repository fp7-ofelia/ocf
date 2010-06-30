from django.contrib.auth.decorators import login_required
from django.views.generic import simple
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from openflow.optin_manager.users.models import UserProfile
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
from openflow.optin_manager.controls.forms import *
from django.db.models import Q
from django.core.urlresolvers import reverse
import logging

logger = logging.getLogger("ControlsViews")

def set_clearinghouse(request):
    error_msg = ""
    if (not request.user.is_staff):
        return HttpResponseRedirect("/dashboard")
            
    ch_users = UserProfile.objects.filter(is_clearinghouse_user=True)
    already_exist = True
    profile = None
    if len(ch_users) == 0:
        already_exist = False
        ch_id = -1
    elif len(ch_users) == 1:
        profile = ch_users[0]
        ch_id = profile.user.id
    else:
        #this shouldn't happen
        return 0
        
    if (request.method == "POST"):
        form = CHUserForm(request.POST)

  
        if (form.is_valid()):
            same_uname = User.objects.filter(username = 
                    request.POST["username"]).exclude(id = ch_id)
            if (len(same_uname) > 0):
                form._errors["general"] = ErrorList(["Username is not unique"])
            else:
                if len(ch_users) == 0:
                    ch_user = User(username=request.POST["username"])
                    ch_user.set_password(request.POST["password1"])
                    ch_user.save()
                    ch_profile = UserProfile.get_or_create_profile(ch_user)
                    ch_profile.is_net_admin = False
                    ch_profile.is_clearinghouse_user = True
                    ch_profile.max_priority_level = 0
                    ch_profile.save()
                else:
                    profile.user.username = request.POST["username"]
                    profile.user.set_password(request.POST["password1"])
                    profile.user.save()
                return HttpResponseRedirect("/dashboard")
    else:
        if len(ch_users) == 1:
            form = CHUserForm(pack_ch_user_info(profile.user))
        else:
            form = CHUserForm()
               
    return simple.direct_to_template(request,
                template = 'openflow/optin_manager/controls/set_clearinghouse.html',
                extra_context = {
                        'error_msg': error_msg,
                        'profile':profile,
                        'form':form,

                 }
        )
        
def set_flowvisor(request):
    if (not request.user.is_staff):
        return HttpResponseRedirect("/dashboard")
            
    fvs = FVServerProxy.objects.all()
    if fvs.count():
        fv = fvs[0]
    else:
        fv = None
        
    if request.method == "POST":
        logger.debug("Received post")
        form = FVServerProxyForm(request.POST, instance=fv)
        if form.is_valid():
            logger.debug("Form is valid")
            fv = form.save()
            return HttpResponseRedirect(reverse("dashboard"))
        logger.debug("Form is invalid: %s" % form.errors)
    else:
        form = FVServerProxyForm(instance=fv)
        
    return simple.direct_to_template(
        request,
        template="openflow/optin_manager/controls/set_flowvisor2.html",
        extra_context={
            "form": form,
        },
    )

#    already_exist = True
#    fv = None
#    if len(fvs) == 0:
#        already_exist = False
#    elif len(fvs) == 1:
#        fv = fvs[0]
#    else:
#        #this shouldn't happen
#        return 0
#        
#    if (request.method == "POST"):
#        pass_form =FVServerFormPassword(request.POST)
#        form = FVServerForm(request.POST) 
#        if (form.is_valid() and pass_form.is_valid()):
#            if len(fvs) == 0:
#                fv = form.save(commit=False)
#                fv.password = request.POST["password1"]
#                if ("verify_certs" in request.POST):
#                    fv.verify_certs = True
#                else:
#                    fv.verify_certs = False
#
#            else:
#                fv.name = request.POST["name"]
#                fv.username = request.POST["username"]
#                fv.password = request.POST["password1"]
#                fv.url = request.POST["url"]
#                fv.max_password_age = request.POST["max_password_age"]
#                if ("verify_certs" in request.POST):
#                    fv.verify_certs = True
#                else:
#                    fv.verify_certs = False
#
#            # try pinging FV to see if it really works:
#            try:
#                data = fv.api.ping("HELLO")
#                if (data != "PONG(%s): HELLO"%fv.username):
#                    form._errors["general"] = \
#                        ErrorList(["Flowvisor not responding as expected"])
#                else:
#                    fv.save()
#                    return HttpResponseRedirect("/dashboard")
#            except:
#                form._errors["general"] = \
#                    ErrorList(["Error pinging Flowvisor: No response"])
#
#    else:
#        if len(fvs)==0:
#            pass_form = FVServerFormPassword()
#            form = FVServerForm()
#        else:
#            pass_form = FVServerFormPassword()
#            form = FVServerForm(instance=fv)  
#
#        
#    return simple.direct_to_template(request,
#                template = 'openflow/optin_manager/controls/set_flowvisor.html',
#                extra_context = {
#                    'form':form,
#                    'pass_form':pass_form,
#                 }
#        )