from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from egeni.clearinghouse.models import AggregateManager, Node, Slice, SliceForm, FlowSpace
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory

def home(request):
    '''Show the list of slices, and form for creating new slice'''

    if request.method == 'POST':
        slice = Slice(owner=request.user, committed=False)
        form = SliceForm(request.POST, instance=slice)
        print "<0>"
        if form.is_valid():
            print "<1>"
            slice = form.save()
            print "<2>"
            return HttpResponseRedirect(slice.get_absolute_url())
        print "<3>"
    else:
        # get reserved and unreserved slices
        form = SliceForm()
        
    reserved_slices = request.user.slice_set.filter(committed__exact=True)
    reserved_ids = reserved_slices.values_list('id', flat=True)
    unreserved_slices = request.user.slice_set.exclude(id__in=reserved_ids)
    
    return render_to_response("clearinghouse/home.html",
                              {'reserved_slices': reserved_slices,
                               'unreserved_slices': unreserved_slices,
                               'form': form})

def slice_detail(request, slice_id):
    slice = get_object_or_404(Slice, pk=slice_id)
    agg_list = AggregateManager.objects.all()
    
    # create a formset to handle all flowspaces
    FSFormSet = inlineformset_factory(Slice, FlowSpace)
    
    if request.method == "POST":
        
        # get all the selected nodes
        for am in agg_list:
            slice.nodes.remove(
                slice.nodes.exclude(
                    id__in=request.POST["am_%s" % am.name]))
            slice.nodes.add(
                Slice.nodes.filter(
                    id__in=request.POST["am_%s" % am.name]).exclude(
                        id__in=slice.nodes.values_list('id', flat=True)))
            
        formset = FSFormSet(request.POST, request.FILES, instance=slice)
        if formset.is_valid():
            formset.save()
            
            # TODO: Request/update slice from agg mgr
            slice.committed = True
            slice.save()
                        
            return HttpResponseRedirect(reverse('home'))
        
    else:
        formset = FSFormSet(instance=slice)
        print "Formset: "
        print formset
        print "forms: "
        for form in formset.forms:
            print form.as_table()
        
    return render_to_response("clearinghouse/slice_detail.html",
                              {'aggmgr_list': agg_list,
                               'slice': slice,
                               'fsformset': formset,
                               })

def resv_sel_nodes(request, slice_id, am_id):
    '''Select nodes from the AM'''
    
    slice = get_object_or_404(Slice, pk=slice_id)
    am = get_object_or_404(AggregateManager, pk=am_id)
    
    if request.method == 'POST':
        # get all the node IDs
        ids = request.POST.keys()
        print "Selected nodes: ", ids
        
        # remove all nodes from the slice and add the new ones
        slice.node_set.all().delete()
    try:
        am.updateRSpec()
    except Exception, e:
        print "Update RSpec Exception"; print e
        return render_to_response("clearinghouse/aggregatemanager_detail.html",
                                  {'am':am,
                                   'error_message':"Error Parsing/Updating the RSpec: %s" % e,
                                   })
    
    return render_to_response("clearinghouse/aggregatemanager_detail.html",
                              {'am':am,
                               })
    
    
def node_detail(request, aggMgr_id, node_id, message=None):
    '''Show the details for a node and show a form to reserve a slice'''
    
    print "node detail: am id: %s, node_id %s" % (aggMgr_id, node_id)
    # get the aggregate manager object
    am = get_object_or_404(AggregateManager, pk=aggMgr_id)
    node = get_object_or_404(Node, pk=node_id)
    
    # get the details
    return render_to_response("clearinghouse/node_detail.html",
                              {'aggMgr':am,
                               'node':node,
                               'message':message})

def delete(request, object_id):
    # get the aggregate manager object
    am = get_object_or_404(AggregateManager, pk=object_id)
    am.delete()
    return HttpResponseRedirect(reverse('index'))

def create(request):
    error_msg = u"No POST data sent."
    if(request.method == "POST"):
        post = request.POST.copy()
        if(post.has_key('name') and post.has_key('url')):
            # Get info
            name = post['name']
            url = post['url']
            key_file = post['key_file'] if post.has_key('key_file') else None
            cert_file = post['cert_file'] if post.has_key('cert_file') else None
            
            new_am = AggregateManager.objects.create(name=name,
                                                     url=url,
                                                     key_file=key_file,
                                                     cert_file=cert_file)
            return HttpResponseRedirect(new_am.get_absolute_url())
        else:
            error_msg = u"Insufficient data. Need at least name and url"
    return HttpResponseServerError(error_msg)

def aggmgr_detail(request, am_id):
    # get the aggregate manager object
    am = get_object_or_404(AggregateManager, pk=am_id)
    if(request.method == "GET"):
        return render_to_response("clearinghouse/aggregatemanager_detail.html",
                                  {'object':am})
        
    elif(request.method == "POST"):
        try:
            am.updateRSpec()
        except Exception, e:
            print "Update RSpec Exception"; print e
            return render_to_response("clearinghouse/aggregatemanager_detail.html",
                                      {'object':am,
                                       'error_message':"Error Parsing/Updating the RSpec: %s" % e,
                                       })
        else:
            am.save()
            return HttpResponseRedirect(am.get_absolute_url())
    else:
        return HttpResponseServerError(u"Unknown method %s" % request.method)

def node_reserve(request, aggMgr_id, node_id):
    # get the aggregate manager object
    am = get_object_or_404(AggregateManager, pk=aggMgr_id)
    message = u"No POST data sent."
    if(request.method == "POST"):
        post = request.POST.copy()
        if(post.has_key('port') 
           and post.has_key('dl_src')
           and post.has_key('dl_dst')
           and post.has_key('dl_type')
           and post.has_key('vlan_id')
           and post.has_key('nw_src')
           and post.has_key('nw_dst')
           and post.has_key('nw_proto')
           and post.has_key('tp_src')
           and post.has_key('tp_dst')):
            # Get info
            message = am.makeReservation(node_id, post)
        else:
            message = u"Insufficient data. Need all fields."
        
        return HttpResponseRedirect()

# TODO test the flowspace form and see what it looks like


