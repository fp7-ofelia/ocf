'''
Created on Oct 6, 2010

@author: jnaous
'''
# TODO: Also show the slice URN
from expedient.clearinghouse.slice.models import Slice
from django.shortcuts import get_object_or_404
from expedient.ui.rspec.forms import UploadRSpecForm
from openflow.plugin.gapi.rspec import create_resv_rspec
from openflow.plugin.gapi import gapi, rspec
from expedient.clearinghouse.geni.models import GENISliceInfo
from expedient.common.messaging.models import DatedMessage
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import simple
from expedient.common.permissions.shortcuts import must_have_permission

TEMPLATE_PATH="rspec"

def home(request, slice_id):
    """Show buttons to download and upload rspecs."""
    
    slice = get_object_or_404(Slice, pk=slice_id)
    info = GENISliceInfo.objects.get(slice=slice)
    slice_urn = info.slice_urn
    
    must_have_permission(
        request.user, slice.project, "can_edit_slices")
    
    if request.method == "POST":
        form = UploadRSpecForm(request.POST, request.FILES)
        if form.is_valid():
            # parse the rspec
            rspec = form.files["rspec"].read()
            gapi.CreateSliver(slice_urn, rspec, request.user)
            DatedMessage.objects.post_message_to_user(
                "Successfully uploaded RSpec.",
                request.user, msg_type=DatedMessage.TYPE_SUCCESS)
            return HttpResponseRedirect(request.path)
    else:
        form = UploadRSpecForm()
        
    return simple.direct_to_template(
        request,
        template=TEMPLATE_PATH+"/home.html",
        extra_context={
            "form": form, "slice_urn": slice_urn, "slice": slice,
        },
    )
    
def download_resv_rspec(request, slice_id):
    slice = get_object_or_404(Slice, pk=slice_id)
    rspec = create_resv_rspec(request.user, slice)
    response = HttpResponse(rspec, mimetype='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=resv_rspec.xml'
    return response

def download_adv_rspec(request):
    adv_rspec = rspec.get_resources(None, True)
    response = HttpResponse(adv_rspec, mimetype='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=adv_rspec.xml'
    return response
