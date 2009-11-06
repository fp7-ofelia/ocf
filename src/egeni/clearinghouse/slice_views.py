from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponseBadRequest,\
    HttpRequest, HttpResponseForbidden
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.core.urlresolvers import reverse
from egeni.clearinghouse.models import *
from django.contrib.auth.decorators import user_passes_test
from django.forms.models import inlineformset_factory
import egeni_api, plc_api
import os
import messaging

LINK_ID_FIELD = "link_id"
NODE_ID_FIELD = "node_id"
POS_FIELD = "pos"

REL_PATH = "."

def can_access(user):
    '''Can the user access the user views?'''
    profile = UserProfile.get_or_create_profile(user)
    return user.is_staff or profile.is_user_admin or profile.is_researcher

def check_access(user, slice):
    '''Can the user edit/view the slice?'''
    users = UserProfile.objects.filter(created_by=user).values_list('user', flat=True)
    return user.is_superuser or user.is_staff or slice.owner == user or slice.owner in users

@user_passes_test(can_access)
def slice_home(request):
    '''Show the list of slices, and form for creating new slice'''
    
    # if the user is posting a create request
    if request.method == 'POST':
        if request.user.is_staff:
            owner_form = SelectResearcherForm(request.POST)
            if owner_form.is_valid():
                owner_profile = owner_form.cleaned_data['researcher_profile']
                owner = owner_profile.user
        elif UserProfile.get_or_create_profile(request.user).is_researcher:
            owner = request.user
        else:
            return HttpResponseForbidden("You don't have permission to create a slice.")

        slice = Slice(owner=owner, committed=False)
        form = SliceNameForm(request.POST, instance=slice)
        if owner and form.is_valid():
            slice = form.save()
            return HttpResponseRedirect(reverse("slice_select_aggregates", kwargs={"slice_id": slice.id}))

    else:
        form = SliceNameForm()
        if request.user.is_staff:
            owner_form = SelectResearcherForm()

    if request.user.is_staff:
        slices = Slice.objects.all()
        show_owner = True
    elif UserProfile.get_or_create_profile(request.user).is_user_admin:
        users = UserProfile.objects.filter(created_by=request.user).values_list('user', flat=True)
        slices = Slice.objects.filter(owner__in=users)
        show_owner = True
    else:
        slices = request.user.slice_set.all()
        show_owner = False
    
    return render_to_response("clearinghouse/slice_home.html",
                              {'slices': slices,
                               'aggMgrs': AggregateManager.objects.all(),
                               'owner_form': owner_form,
                               'show_owner': show_owner,
                               'form': form})

@user_passes_test(can_access)
def slice_select_aggregates(request, slice_id):
    '''Show a list of Aggregates and select some'''
    slice = get_object_or_404(Slice, pk=slice_id)
    if not check_access(request.user, slice):
        return HttpResponseForbidden("You don't have permission to access this slice.")
    
    print "%s" % request.method
    
    if request.method == 'GET':
        am_list = AggregateManager.objects.all()
        return render_to_response("clearinghouse/slice_select_aggregates.html",
                                  {'am_list': am_list,
                                   'slice': slice,
                                   })
        
    elif request.method == 'POST':
        am_ids = request.POST.getlist("am")
        ams = AggregateManager.objects.filter(pk__in=am_ids)
        [slice.aggMgrs.add(am) for am in ams]
        slice.save()
        return HttpResponseRedirect(reverse("slice_select_topo", kwargs={"slice_id": slice.id}))
    
    return HttpResponseNotAllowed("GET", "POST")

@user_passes_test(can_access)
def slice_select_topo(request, slice_id):
    slice = get_object_or_404(Slice, pk=slice_id)
    if not check_access(request.user, slice):
        return HttpResponseForbidden("You don't have permission to access this slice.")

    if request.method == "POST":
        link_ids = request.POST.getlist(LINK_ID_FIELD)
        node_ids = request.POST.getlist(NODE_ID_FIELD)
        positions = request.POST.getlist(POS_FIELD)
        
        # collect the positions
        pos_dict = {}
        for p in positions:
            id, xy = p.split(":::")
            x, y = xy.split(",")
            pos_dict[id] = (x, y)
        NodeSliceGUI.update_pos(pos_dict, slice)
        
        # delete old links and nodes
        LinkSliceStatus.objects.filter(
            slice=slice).exclude(link__pk__in=link_ids).delete()
        NodeSliceStatus.objects.filter(
            slice=slice).exclude(node__pk__in=node_ids).delete()
        
        # create new links and ids
        for id in link_ids:
            print "Link: %s" % id
            link = get_object_or_404(Link, pk=id)
            through, created = LinkSliceStatus.objects.get_or_create(
                                    slice=slice,
                                    link=link,
                                    defaults={'reserved': False,
                                              'removed': False,
                                              'has_error': False,
                                              }
                                    )
            
        for id in node_ids:
            print "Node: %s" % id
            node = get_object_or_404(Node, pk=id)
            through, created = NodeSliceStatus.objects.get_or_create(
                                    slice=slice,
                                    node=node,
                                    defaults={'reserved': False,
                                              'removed': False,
                                              'has_error': False,
                                              }
                                    )
        
        slice.save()
        
        return HttpResponseRedirect(reverse('slice_select_openflow', args=[slice_id]))

    elif request.method == "GET":
#        xml = slice_get_topo_string(slice)
        return render_to_response("clearinghouse/slice_select_topo.html",
                                  {'slice': slice,
#                                   'topo_xml': xml,
                                   })
    else:
        return HttpResponseNotAllowed("GET", "POST")

@user_passes_test(can_access)
def slice_select_openflow(request, slice_id):
    slice = get_object_or_404(Slice, pk=slice_id)
    if not check_access(request.user, slice):
        return HttpResponseForbidden("You don't have permission to access this slice.")

    # create a formset to handle all flowspaces
    FSFormSet = inlineformset_factory(Slice, FlowSpace)
    
    if request.method == "POST":
        if "type" not in request.POST:
            return HttpResponseBadRequest("Missing field 'type'")
        
        type = request.POST["type"]
        form = SliceURLForm(request.POST, instance=slice)
        
        if form.is_valid():
            slice = form.save()
            
        if type == "advanced":
            formset = FSFormSet(request.POST, request.FILES, instance=slice)
            if formset.is_valid() and form.is_valid():
                formset.save()
                slice.committed = False
                slice.save()
                return HttpResponseRedirect(reverse("slice_resv_summary", args=[slice_id]))
        else:
            slice.flowspace_set.all().delete()
            if type == "http":
                fs = FlowSpace(slice=slice,
                               policy=FlowSpace.TYPE_ALLOW,
                               dl_type="2048",
                               nw_proto="6",
                               tp_src="80",
                               )
                fs.save()
                fs = FlowSpace(slice=slice,
                               policy=FlowSpace.TYPE_ALLOW,
                               dl_type="2048",
                               nw_proto="6",
                               tp_dst="80",
                               )
                fs.save()
            elif type == "ip":
                fs = FlowSpace(slice=slice,
                               policy=FlowSpace.TYPE_ALLOW,
                               dl_type="2048",
                               )
                fs.save()
            elif type == "tcp":
                fs = FlowSpace(slice=slice,
                               policy=FlowSpace.TYPE_ALLOW,
                               dl_type="2048",
                               nw_proto="6",
                               )
                fs.save()
            elif type == "special":
                fs = FlowSpace(slice=slice,
                               policy=FlowSpace.TYPE_ALLOW,
                               dl_type="2048",
                               nw_proto="6",
                               tp_src="10001",
                               )
                fs.save()
                fs = FlowSpace(slice=slice,
                               policy=FlowSpace.TYPE_ALLOW,
                               dl_type="2048",
                               nw_proto="6",
                               tp_dst="10001",
                               )
                fs.save()
            else:
                return HttpResponseBadRequest("Unexpected value of packet type %s" % type)
            
            slice.save()
            formset = FSFormSet(instance=slice)
            if form.is_valid():
                return HttpResponseRedirect(reverse("slice_resv_summary", args=[slice_id]))
    
    elif request.method == "GET":
        formset = FSFormSet(instance=slice)
        form = SliceURLForm(instance=slice)

    else:
        return HttpResponseNotAllowed("GET", "POST")
        
    return render_to_response("clearinghouse/slice_select_openflow.html",
                              {'slice': slice,
                               'fsformset': formset,
                               'form': form,
                               })

@user_passes_test(can_access)
def slice_resv_summary(request, slice_id):
    slice = get_object_or_404(Slice, pk=slice_id)
    if not check_access(request.user, slice):
        return HttpResponseForbidden("You don't have permission to access this slice.")

    print "Doing resv summary"

    slice.committed = False
    slice.save()
    if request.method == "GET":
        return render_to_response("clearinghouse/slice_resv_summary.html",
                                  {'slice': slice})
        
    elif request.method == "POST":
        # Delete the old slice from the AMs so we can create it again
        for am in slice.aggMgrs.all():
            try:
                if am.type == AggregateManager.TYPE_OF:
                    egeni_api.delete_slice(am.url, slice_id)
                elif am.type == AggregateManager.TYPE_PL:
                    plc_api.delete_slice(am.url, slice_id)
            except Exception, e:
                text = "Error deleting slice %s to re-reserve from Aggregate %s: %s. Will still remove from DB." % (slice.name, am.name, e)
                print text
                messaging.add_msg_for_user(request.user, text, DatedMessage.TYPE_ERROR)
                return render_to_response("clearinghouse/slice_resv_summary.html",
                                          {'slice': slice,
                                           'error_message': "Error reserving slice"})
        
        # get the RSpec of the Slice for each am and reserve
        commit = True
        for am in AggregateManager.objects.all():
            try:
                am.reserve_slice(slice)
            except Exception, e:
                text = "Error reserving slice %s in Aggregate %s: %s." % (slice.name, am.name, e)
                print text
                commit = False
                messaging.add_msg_for_user(request.user, text, DatedMessage.TYPE_ERROR)
                return render_to_response("clearinghouse/slice_resv_summary.html",
                                          {'slice': slice,
                                           'error_message': "Error reserving slice"})
        
        slice.committed = commit
        slice.save()
        return HttpResponseRedirect(reverse('slice_resv_confirm', args=(slice.id,)))

    else:
        return HttpResponseNotAllowed("GET", "POST")
    
@user_passes_test(can_access)
def slice_resv_confirm(request, slice_id):
    slice = get_object_or_404(Slice, pk=slice_id)
    if not check_access(request.user, slice):
        return HttpResponseForbidden("You don't have permission to access this slice.")

    if request.method == "GET":
        return render_to_response("clearinghouse/slice_resv_summary.html",
                                  {'slice': slice,
                                   'confirm': True,
                                   })
    return HttpResponseNotAllowed("GET")

@user_passes_test(can_access)
def slice_delete(request, slice_id):
    '''Confirm delete and delete slice'''
    slice = get_object_or_404(Slice, pk=slice_id)
    if not check_access(request.user, slice):
        return HttpResponseForbidden("You don't have permission to access this slice.")

    for am in AggregateManager.objects.all():
        try:
            if am.type == AggregateManager.TYPE_OF:
                egeni_api.delete_slice(am.url, slice.id)
            elif am.type == AggregateManager.TYPE_PL:
                plc_api.delete_slice(am.url, slice.id)
        except Exception, e:
            print e
            traceback.print_exc()
            text = "Error deleting slice %s from Aggregate %s. Will still remove from DB." % (slice.name, am.name)
            print text
            messaging.add_msg_for_user(request.user, text, DatedMessage.TYPE_ERROR)
                
    slice.delete()
    return HttpResponseRedirect(reverse('slice_home'))
    
def slice_get_plugin(request, slice_id):
    jar = open("%s/../plugin.jar" % REL_PATH, "rb").read()
    return HttpResponse(jar, mimetype="application/java-archive")

@user_passes_test(can_access)
def slice_get_topo_xml(request, slice_id):
    slice = get_object_or_404(Slice, pk=slice_id)
    if not check_access(request.user, slice):
        return HttpResponseForbidden("You don't have permission to access this slice.")
    
    if request.method == "GET":
        xml = slice_get_topo_string(slice)
        return HttpResponse(xml, mimetype="text/xml")
    else:
        return HttpResponseNotAllowed("GET")

def slice_get_topo_string(slice):
    for am in AggregateManager.objects.all():
        try:
            am.updateRSpec()
        except Exception, e:
            messaging.add_msg_for_user(
                request.user,
                "Error updating RSpec for Aggregate %s: %s" % (am.name, e),
                DatedMessage.TYPE_ERROR)
    print "Done update"
    # get all the local nodes
    nodes = Node.objects.all().exclude(
                is_remote=True).filter(
                    aggMgr__id__in=slice.aggMgrs.values_list('id', flat=True))
    print nodes
    nodes_dict = {}
    for n in nodes:
        try:
            nsg = NodeSliceGUI.objects.get(slice=slice,
                                           node=n)
        except NodeSliceGUI.DoesNotExist:
            x = n.x or -1
            y = n.y or -1
        
        else:
            x = nsg.x
            y = nsg.y
                    
        nodes_dict[n.nodeId] = {'node': n,
                                'x': x,
                                'y': y,
                                }

    # get all the local links
    links = Link.objects.filter(
                src__ownerNode__is_remote=False,
                dst__ownerNode__is_remote=False)

    return render_to_string("plugin/flash-xml.xml",
                           {'nodes_dict': nodes_dict,
                            'links': links,
                            'slice': slice})
