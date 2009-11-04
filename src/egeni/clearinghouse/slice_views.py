from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponseBadRequest,\
    HttpRequest, HttpResponseForbidden
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.core.urlresolvers import reverse
from egeni.clearinghouse.models import *
from django.forms.models import inlineformset_factory
import egeni_api, plc_api
import os

LINK_ID_FIELD = "link_id"
NODE_ID_FIELD = "node_id"
XPOS_FIELD = "x-pos"
YPOS_FIELD = "y-pos"

REL_PATH = "."

def slice_home(request):
    '''Show the list of slices, and form for creating new slice'''

    if request.method == 'POST':
        if not request.POST.has_key("action"):
            return HttpResponseBadRequest("Missing field action")
        
        if request.POST["action"] == "delete_slice":
            slice_ids = request.POST.getlist('del_sel')
            slices = request.user.slice_set.filter(id__in=slice_ids)
            for am in AggregateManager.objects.all():
                for slice in slices:
                    try:
                        if am.type == AggregateManager.TYPE_OF:
                            egeni_api.delete_slice(am.url, slice.id)
                        elif am.type == AggregateManager.TYPE_PL:
                            plc_api.delete_slice(am.url, slice.id)
                    except Exception, e:
                        print e
                        traceback.print_exc()
                        print "Error deleting slice. Will still remove from DB."
            slices.delete()
            return HttpResponseRedirect(reverse('slice_home'))

        elif request.POST["action"] == "create_slice":
            slice = Slice(owner=request.user, committed=False)
            form = SliceForm(request.POST, instance=slice)
            if form.is_valid():
                slice = form.save()
                return HttpResponseRedirect(slice.get_absolute_url())
        
        else:
            return HttpResponseBadRequest(
                "Unknown action value: %s" % request.POST["action"])
    else:
        # get reserved and unreserved slices
        form = SliceForm()
        
        reserved_slices = request.user.slice_set.filter(committed=True)
        unreserved_slices = request.user.slice_set.filter(committed=False)
        
        do_del = request.user.slice_set.count() > 0
        return render_to_response("clearinghouse/slice_home.html",
                                  {'do_del': do_del,
                                   'reserved_slices': reserved_slices,
                                   'unreserved_slices': unreserved_slices,
                                   'aggMgrs': AggregateManager.objects.all(),
                                   'form': form})          

def slice_detail(request, slice_id):
    slice = get_object_or_404(Slice, pk=slice_id)
    if slice.owner != request.user:
        return HttpResponseForbidden()
    agg_list = AggregateManager.objects.all()
    
    # create a formset to handle all flowspaces
    FSFormSet = inlineformset_factory(Slice, FlowSpace)
    
    print "<xx>"
    
    if request.method == "POST":
        print "<yy>"
        # get all the selected nodes
        for am in agg_list:
            # remove from slice the nodes that are not in the post
            nodes = slice.nodes.exclude(
                nodeId__in=request.POST.getlist("am_%s" % am.id))
            [slice.nodes.remove(n) for n in nodes]
            
            # add to slice nodes that are in post but not in slice
            nodes = am.local_node_set.filter(
                nodeId__in=request.POST.getlist("am_%s" % am.id))
            nodes = nodes.exclude(
                nodeId__in=slice.nodes.values_list('nodeId', flat=True))
            print "nodes: %s" % nodes
            [slice.nodes.add(n) for n in nodes]
            
        formset = FSFormSet(request.POST, request.FILES, instance=slice)
        if formset.is_valid():
            formset.save()
            
            slice.committed = True
            slice.save()
            
            # TODO: Do reservation here
            
            return HttpResponseRedirect(reverse('slice_home'))
        
    else:
        print "<zz>"
        for am in agg_list:
            print "<aa>"
            am.updateRSpec()
        formset = FSFormSet(instance=slice)
        print "Slice nodeIds: %s" % slice.nodes.values_list('nodeId', flat=True)
    
#        print "Formset: "
#        print formset
#        print "forms: "
#        for form in formset.forms:
#            print form.as_table()
        
    return render_to_response("clearinghouse/slice_detail.html",
                              {'aggmgr_list': agg_list,
                               'slice': slice,
                               'fsformset': formset,
                               })

def slice_flash_detail(request, slice_id, confirm=False):
    slice = get_object_or_404(Slice, pk=slice_id)
    if slice.owner != request.user:
        return HttpResponseForbidden()
    
    # create a formset to handle all flowspaces
    FSFormSet = inlineformset_factory(Slice, FlowSpace)
    
    print "<xx> request method %s" % request.method
    
    if request.method == "POST":
#        if NODE_ID_FIELD not in request.POST or LINK_ID_FIELD not in request.POST:
#            return HttpResponseBadRequest("Missing fields %s or %s" 
#                                          % (LINK_ID_FIELD, NODE_ID_FIELD))
        
        formset = FSFormSet(request.POST, request.FILES, instance=slice)
        if not formset.is_valid():
            return HttpResponseBadRequest("Form is invalid")
        
        link_ids = request.POST.getlist(LINK_ID_FIELD)
        node_ids = request.POST.getlist(NODE_ID_FIELD)
        x_positions = request.POST.getlist(XPOS_FIELD)
        y_positions = request.POST.getlist(YPOS_FIELD)
        
        print "xpos: %s" % x_positions
        print "ypos: %s" % y_positions
        
        # Update the positions of the nodes
        for id_x in x_positions:
            id, x = id_x.split(":::")
            try:
                n = Node.objects.get(nodeId=id)
            except Node.DoesNotExist:
                print "!!!! In reserve Node %s does not exist" % id
                continue
            
            nsg, created = NodeSliceGUI.objects.get_or_create(
                                slice=slice,
                                node=n,
                                defaults={'x': x,
                                          'y': -1}
                                )
            nsg.x = x
            nsg.save()
            
            if not n.x:
                n.x = x
                n.save()
            
        for id_y in y_positions:
            id, y = id_y.split(":::")
            try:
                n = Node.objects.get(nodeId=id)
            except Node.DoesNotExist:
                print "!!!! In reserve Node %s does not exist" % id
                continue
            
            nsg, created = NodeSliceGUI.objects.get_or_create(
                                slice=slice,
                                node=n,
                                defaults={'x': -1,
                                          'y': y}
                                )
            nsg.y = y
            nsg.save()

            if not n.y:
                n.y = y
                n.save()
        
        # TODO: Delete all the old NodeSliceGUIs
        
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
            if created:
                print "Link ID: %s new in slice" % id
            else:
                print "Link ID: %s already seen" % id
            
        node_slice_set = []
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
            if created:
                print "Node ID: %s new in slice" % id
            else:
                print "Node ID: %s already seen" % id
                
            node_slice_set.append(through)

        formset.save()
        
        # Delete the old slice so we can create it again
        if slice.committed:
            for am in AggregateManager.objects.all():
                if am.type == AggregateManager.TYPE_OF:
                    egeni_api.delete_slice(am.url, slice_id)
                elif am.type == AggregateManager.TYPE_PL:
                    plc_api.delete_slice(am.url, slice_id)
        
        slice.committed = False
        slice.save()
        
        # get the RSpec of the Slice for each am and reserve
        for am in AggregateManager.objects.all():
            if am.type == AggregateManager.TYPE_OF:
                rspec = render_to_string("rspec/egeni-rspec.xml",
                                         {"node_set": slice.nodes.filter(aggMgr=am),
                                          "am": am,
                                          "fs_flds": ["dl_src",
                                                      "dl_dst",
                                                      "dl_type",
                                                      "vlan_id",
                                                      "nw_src",
                                                      "nw_dst",
                                                      "nw_proto",
                                                      "tp_src",
                                                      "tp_dst",
                                                      ],
                                          "slice": slice})
                errors = egeni_api.reserve_slice(am.url, rspec, slice_id);
        
                # TODO: Parse errors here
                
            elif am.type == AggregateManager.TYPE_PL:
                nodes_dict = {}
                node_set = slice.nodes.filter(aggMgr=am)
                for node in node_set:
                    netspec = node.extra_context.split("=")[1]
                    if not nodes_dict.has_key(netspec):
                        nodes_dict[netspec] = []
                    nodes_dict[netspec].append(node)
                print "Nodes dict: %s" % nodes_dict
                rspec = render_to_string("rspec/pl-rspec.xml",
                                         {"node_slice_set": node_slice_set,
                                          "slice": slice,
                                          "nodes_dict": nodes_dict,
                                          })
                errors = plc_api.reserve_slice(am.url, rspec, slice_id)
                # TODO: parse pl errors
        
        slice.committed = True
        slice.save()
        return HttpResponseRedirect(reverse('slice_resv_confirm', args=[slice_id]))

    elif request.method == "GET":
#        for am in agg_list:
#            print "<aa>"
#            am.updateRSpec()
        formset = FSFormSet(instance=slice)
        xml = slice_get_topo_string(slice)
        return render_to_response("clearinghouse/slice_flash_detail.html",
                                  {'slice': slice,
                                   'fsformset': formset,
                                   'topo_xml': xml,
                                   'confirm': confirm,
                                   })
    else:
        return HttpResponseNotAllowed("GET", "POST")
    
def slice_resv_confirm(request, slice_id):
    return slice_flash_detail(request, slice_id, True)

def slice_get_img(request, slice_id, img_name):
    image_data = open("%s/img/%s" % (REL_PATH, img_name), "rb").read()
    return HttpResponse(image_data, mimetype="image/png")

def slice_get_plugin(request, slice_id):
    jar = open("%s/../plugin.jar" % REL_PATH, "rb").read()
    return HttpResponse(jar, mimetype="application/java-archive")

def slice_get_xsd(request, slice_id):
    xsd = open("%s/plugin.xsd" % REL_PATH, "rb").read()
    return HttpResponse(xsd, mimetype="application/xml")    

def slice_get_topo(request, slice_id):
    slice = get_object_or_404(Slice, pk=slice_id)
    if slice.owner != request.user:
        return HttpResponseForbidden()
    print "Doing topo view"
    
    if request.method == "GET":
        xml = slice_get_topo_string(slice)
        return HttpResponse(xml, mimetype="text/xml")
    else:
        return HttpResponseNotAllowed("GET")

def slice_get_topo_string(slice):
    for am in AggregateManager.objects.all():
        am.updateRSpec()
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
