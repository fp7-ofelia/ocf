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
    if (not request.user.is_staff):
        return HttpResponseRedirect("/dashboard")
            
    ch_users = UserProfile.objects.filter(is_clearinghouse_user=True)
    profile = None
    if len(ch_users) == 1:
        profile = ch_users[0]

    elif ch_users.count() > 1:
        #this shouldn't happen
        logger.debug("More than one clearinghouse user in OM!!!")
        raise Exception("There are more than one clearinghouse user! Unexpected error.")
        
    if (request.method == "POST"):
        form = CHUserForm(request.POST)
        if (form.is_valid()):
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
        template="openflow/optin_manager/controls/set_flowvisor.html",
        extra_context={
            "form": form,
        },
    )

