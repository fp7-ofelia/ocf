# Create your views here.
from django.http import *
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from OM import flowspace
from OM.flowspace import forms
from OM.flowspace.models import OptedInFlowSpace, AdminFlowSpace, RequestedAdminFlowSpace, RequestedUserFlowSpace
from OM.flowspace.helper import IPRangeToString

@login_required
def view_opt_in(request):
    #return HttpResponse("view opt in")
    table = []
    fs = OptedInFlowSpace.objects.filter(user=request.user)
    for fs_elem in fs:
        ip_src = IPRangeToString(fs_elem.ip_src_s, fs_elem.ip_src_e)
        ip_dst = IPRangeToString(fs_elem.ip_dst_s, fs_elem.ip_dst_e)
        row = [fs_elem.id , ip_src , ip_dst]
        table.append(row)
    return render_to_response('flowspace/view.html', {'table':table , 'username':request.user.username})
    

@login_required
def add_opt_in(request):
    pass