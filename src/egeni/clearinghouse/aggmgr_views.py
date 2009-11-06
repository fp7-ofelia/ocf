from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponseBadRequest,\
    HttpRequest, HttpResponseForbidden
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.core.urlresolvers import reverse
from egeni.clearinghouse.models import *
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import list_detail, create_update

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
            return HttpResponseRedirect(reverse("aggmgr_saved", args=(am.id,)))
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
    print "detail for am %s" % am.name
    
    if not request.user.is_staff and am.owner != request.user:
        return HttpResponseForbidden()
    
    if(request.method == "GET"):
        print "Get detail for am %s" % am.name
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
        print "Done get"
    
    elif(request.method == "POST"):
        print "Post detail for am %s" % am.name
        form = AggregateManagerForm(request.POST, instance=am)
        print "Validating"
        if form.is_valid():
            print "Validation done"
            form.save()
            print "Done post"
            return HttpResponseRedirect(reverse("aggmgr_saved", args=(am.id,)))
        print "Form error"
    else:
        return HttpResponseNotAllowed("GET", "POST")

    return render_to_response("clearinghouse/aggregatemanager_detail.html",
                              {'am':am,
                               'form': form,
                               })
    
@user_passes_test(can_access)
def saved(request, am_id):
    am = get_object_or_404(AggregateManager, pk=am_id)
    
    if not request.user.is_staff and am.owner != request.user:
        return HttpResponseForbidden()
    
    return render_to_response("clearinghouse/aggregatemanager_saved.html",
                              {'am': am},
                              )

@user_passes_test(can_access)
def delete(request, am_id):
    am = get_object_or_404(AggregateManager, pk=am_id)
    if not request.user.is_staff and am.owner != request.user:
        return HttpResponseForbidden()
    
    return create_update.delete_object(request,
                                       AggregateManager,
                                       reverse("aggmgr_admin_home"),
                                       am_id)

