from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponseBadRequest,\
    HttpRequest, HttpResponseForbidden
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.core.urlresolvers import reverse
from egeni.clearinghouse.models import *
from django.contrib.auth.decorators import user_passes_test

def can_access(user):
    '''Can the user access the aggregate manager views?'''
    profile = UserProfile.get_or_create_profile(user)
    return user.is_staff or profile.is_aggregate_admin

@user_passes_test(can_access)
def home(request):
    '''show list of agg mgrs and form to create new one'''
    
    if request.user.is_staff:
        am_list = AggregateManager.objects.all()
    else:
        am_list = AggregateManager.objects.filter(owner=request.user)

    if request.method == "GET":
        form = AggregateManagerForm()
        
    elif request.method == "POST":
        am = AggregateManager(owner=request.user)
        form = AggregateManagerForm(request.POST, instance=am)
        if form.is_valid():
            am = form.save()
            return HttpResponseRedirect(am.get_absolute_url())
    else:
        return HttpResponseNotAllowed("GET", "POST")
    
    return render_to_response('clearinghouse/aggregatemanager_list.html',
                              {'am_list': am_list,
                               'form': form,
                               })

@user_passes_test(can_access)
def detail(request, am_id):
    # get the aggregate manager object
    am = get_object_or_404(AggregateManager, pk=am_id)
    
    if not request.user.is_staff and am.owner != request.user:
        return HttpResponseForbidden()
    
    if(request.method == "GET"):
        form = AggregateManagerForm(instance=am)
        try:
            am.updateRSpec()
        except Exception, e:
            print "Update RSpec Exception"; print e
            return render_to_response("clearinghouse/aggregatemanager_detail.html",
                                      {'am':am,
                                       'form': form,
                                       'error_message':"Error Parsing/Updating the RSpec: %s" % e,
                                       })
    
    elif(request.method == "POST"):
        form = AggregateManagerForm(request.POST, instance=am)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("aggmgr_saved",
                                                kwargs={'extra_context': {'am': am}}))
    else:
        return HttpResponseNotAllowed("GET", "POST")

    return render_to_response("clearinghouse/aggregatemanager_detail.html",
                              {'am':am,
                               'form': form,
                               })