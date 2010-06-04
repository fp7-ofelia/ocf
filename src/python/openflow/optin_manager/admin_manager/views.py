# Create your views here.
from django.contrib.auth.decorators import login_required
from django.views.generic import simple
from openflow.optin_manager.flowspace.models import AdminFlowSpace
from openflow.optin_manager.users.models import UserProfile
from openflow.optin_manager.flowspace.forms import AdminOptInForm
from openflow.optin_manager.flowspace.helper import multi_fs_intersect,make_flowspace

@login_required
def promote_to_admin(request):
    
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
            for admin in admins_list:
                adminfs = AdminFlowSpace.objects.filter(user=admin.user)
                f = multi_fs_intersect(adminfs,[optedFS])
                if (f):
                    #check if f is equal to opted fs
                