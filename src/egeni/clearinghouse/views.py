from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponseServerError
from django.core.urlresolvers import reverse
from egeni.clearinghouse.models import AggregateManager
from geniLight.geniLight_client import GeniLightClient
from django.core.urlresolvers import reverse
import traceback

def node_detail(request, aggMgr_id, node_id, message=None):
    '''Show the details for a node and show a form to reserve a slice'''
    
    print "node detail: am id: %s, node_id %s" % (aggMgr_id, node_id)
    # get the aggregate manager object
    am = get_object_or_404(AggregateManager, pk=aggMgr_id)
    am.updateRSpec()
    am.save()
    
    # get the details
    node_tuple = am.getNodeDetail(node_id)
    if(node_tuple == None):
        return HttpResponseServerError(u"Node %s not found!" % node_id)
    
    return render_to_response("clearinghouse/node_detail.html",
                              {'aggMgr':am,
                               'node_id':node_id,
                               'node_tuple':node_tuple,
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
                                                     cert_file=cert_file,
                                                     rspec="")
            return HttpResponseRedirect(reverse('am_details', args=(new_am.id,)))
        else:
            error_msg = u"Insufficient data. Need at least name and url"
    return HttpResponseServerError(error_msg)

def aggmgr_update(request, am_id):
    if(request.method == "POST"):
        # get the aggregate manager object
        am = get_object_or_404(AggregateManager, pk=am_id)
        am.updateRSpec()
        am.save()
        return HttpResponseRedirect(reverse('am_details', args=(am.id,)))
    else:
        return HttpResponseServerError(u"This page can only be accessed with a POST")

def aggmgr_detail(request, am_id):
    # get the aggregate manager object
    am = get_object_or_404(AggregateManager, pk=am_id)
    
    # get the list of switches and their remote connections
    nodes = None
    try:
        nodes = am.getSwitchesInfo()
    except Exception, e:
        print "Exception! %s" % e
        return render_to_response('clearinghouse/aggregatemanager_detail.html',
                                  {'object': am,
                                   'error_message': 'Could not parse RSpec'})
    else:
        return render_to_response('clearinghouse/aggregatemanager_detail.html',
                                  {'object': am,
                                   'nodes': nodes})

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
        
        return HttpResponseRedirect(reverse('node_details', 
                                            args=(am.id, node_id, message)))



