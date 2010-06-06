from django.contrib.auth.decorators import login_required
from django.views.generic import simple
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from openflow.optin_manager.users.models import UserProfile
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
from openflow.optin_manager.controls.forms import *

def set_clearinghouse(request):
    if (not request.user.is_staff):
        return HttpResponseRedirect("/dashboard")
            
    ch_users = UserProfile.objects.filter(is_clearinghouse_user=True)
    already_exist = True
    profile = None
    if len(ch_users) == 0:
        already_exist = False
    elif len(ch_users) == 1:
        profile = ch_users[0]
    else:
        #this shouldn't happen
        return 0
        
    if (request.method == "POST"):
        if len(ch_users) == 0:
            ch_user = User(username=request.POST["username"],
                                first_name=request.POST["first_name"],
                                last_name=request.POST["last_name"],
                                email=request.POST["email"])
            ch_user.set_password(request.POST["password"])
            ch_user.save()
            ch_profile = UserProfile.get_or_create_profile(ch_user)
            ch_profile.is_net_admin = False
            ch_profile.is_clearinghouse_user = True
            ch_profile.max_priority_level = 0
            ch_profile.save()
        else:
            profile.user.username = request.POST["username"]
            profile.user.set_password(request.POST["password"])
            profile.user.email = request.POST["email"]
            profile.user.first_name = request.POST["first_name"]
            profile.user.last_name = request.POST["last_name"]
            profile.user.save()
        return HttpResponseRedirect("/dashboard")
    else:
        return simple.direct_to_template(request,
                template = 'openflow/optin_manager/controls/set_clearinghouse.html',
                extra_context = {
                        'profile':profile,
                        'already_exist':already_exist, 
                 }
        )
        
def set_flowvisor(request):
    if (not request.user.is_staff):
        return HttpResponseRedirect("/dashboard")
            
    fvs = FVServerProxy.objects.all()
    already_exist = True
    fv = None
    if len(fvs) == 0:
        already_exist = False
    elif len(fvs) == 1:
        fv = fvs[0]
    else:
        #this shouldn't happen
        return 0
        
    if (request.method == "POST"):
        form =FVServerForm(request.POST)
        if (form.is_valid()):
            if len(fvs) == 0:
                fv = FVServerProxy(name = request.POST["name"],
                               username=request.POST["username"],
                               password=request.POST["password"],
                               url=request.POST["url"],
                               max_password_age=request.POST["max_password_age"],
                               )
                if ("verify_certs" in request.POST):
                    fv.verify_certs = True
                else:
                    fv.verify_certs = False
                fv.save()
            else:
                fv.name = request.POST["name"]
                fv.username = request.POST["username"]
                fv.password = request.POST["password"]
                fv.url = request.POST["url"]
                fv.max_password_age = request.POST["max_password_age"]
                if ("verify_certs" in request.POST):
                    fv.verify_certs = True
                else:
                    fv.verify_certs = False
                fv.save()
            return HttpResponseRedirect("/dashboard")
    else:
        if len(fvs) == 1:
            form = FVServerForm(pack_fvserver_info(fv))
        else:
            form = FVServerForm()

        
    return simple.direct_to_template(request,
                template = 'openflow/optin_manager/controls/set_flowvisor.html',
                extra_context = {
                    'form':form,
                 }
        )