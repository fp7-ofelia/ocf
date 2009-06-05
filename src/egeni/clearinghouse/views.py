from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponseServerError
from django.core.urlresolvers import reverse
from egeni.clearinghouse.models import AggregateManager
from geniLight.geniLight_client import GeniLightClient
from django.core.urlresolvers import reverse
import traceback

def node_detail(request, aggMgr_id, node_id):
    '''Show the details for a node and show a form to reserve a slice'''
    
    # get the aggregate manager object
    am = get_object_or_404(AggregateManager, pk=aggMgr_id)
    
    return render_to_response("clearinghouse/node_detail.html",
                              {'aggMgr':am,
                               'node_id':node_id})

def delete(request, object_id):
    # get the aggregate manager object
    am = get_object_or_404(AggregateManager, pk=object_id)
    am.delete()
    return HttpResponseRedirect(reverse('index'))

def call_func(request, object_id):
    # get the aggregate manager object
    am = get_object_or_404(AggregateManager, pk=object_id)
    client = GeniLightClient(am.url, am.key_file, am.cert_file)    
    post = request.POST
    try:
        func_name = post['choice']
    except(KeyError):
        return render_to_response("clearinghouse/aggregatemanager_detail.html",
                                  {'object': am,
                                   'error_message': "You didn't select a choice",},)
    else:
        # check if the function name is known
#        if(hasattr(client, func_name) and callable(getattr(client, func_name))):
#            if(func_name == "list_nodes"):
#                args = (None)
#            else:
#                args = ()
            
#            result = getattr(client, func_name)(args)
        if(func_name == "list_nodes"):
            result = client.list_nodes(None)
        elif(func_name == "test_func_call"):
            result = client.test_func_call()
        else:
            return render_to_response("clearinghouse/aggregatemanager_detail.html",
                                      {'object': am,
                                       'error_message': "Unknown Function: %s" % func_name,},)
                
        return render_to_response('clearinghouse/aggregatemanager_detail.html',
                                  {'object': am,
                                   'func_name': func_name,
                                   'result': result,
                                   })

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
            
            # Only check the agg mgr exists if the name doesn't start with test
            if(name.startswith('test')):
                client = GeniLightClient(am.url, am.key_file, am.cert_file)
#                try:
                client.list_nodes(None)
#                except Exception, inst:
#                    traceback.print_exc()
#                    print inst
#                    error_msg = u"Error doing list_nodes from aggregate manager at %s." % url
#                    return HttpResponseServerError(error_msg)
                    
            new_am = AggregateManager.objects.create(name=name,
                                                     url=url,
                                                     key_file=key_file,
                                                     cert_file=cert_file)
            return HttpResponseRedirect(reverse('details', args=(new_am.id,)))
        else:
            error_msg = u"Insufficient data. Need at least name and url"
    return HttpResponseServerError(error_msg)
