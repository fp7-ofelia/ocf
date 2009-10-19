from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from egeni.clearinghouse.models import *
from django.forms.models import inlineformset_factory
import os

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
        
    reserved_slices = request.user.slice_set.filter(committed=True)
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
            
            return HttpResponseRedirect(reverse('home'))
        
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

def slice_flash_detail(request, slice_id):
    slice = get_object_or_404(Slice, pk=slice_id)
    agg_list = AggregateManager.objects.all()
    
    # create a formset to handle all flowspaces
    FSFormSet = inlineformset_factory(Slice, FlowSpace)
    
    print "<xx>"
    
    if request.method == "POST":
        
        try:
            action = request.POST["action"]
        
            if action == "link" or action == "node":
                
                selected = request.POST.get("selected") == "True"
                id = request.POST.get(action+"_id")
                
                if action == "link":
                    model = Link
                    through_type = LinkSliceStatus
                else:
                    model = Node
                    through_type = NodeSliceStatus
                
                obj = get_object_or_404(model, pk=id)

                kwargs = {"slice": slice,
                          action: obj,
                          "defaults":{'reserved': False,
                                      'removed': False}}
                through, created = through_type.objects.get_or_create(**kwargs)

                through.removed = not selected
                through.save()
                
            elif action == "reset":
                link_statuses = LinkSliceStatus.objects.exclude(
                                    reserved=True, removed=False)
                [l.delete for l in link_statuses]
                
                node_statuses = NodeSliceStatus.objects.exclude(
                                    reserved=True, removed=False)
                [n.delete for n in node_statuses]
                
            elif action == "reserve":
                # get the RSpec of the Slice
                rspec = render_to_string("rspec/egeni-rspec.xml",
                                         {"node_set": slice.nodes.all(),
                                          "slice": slice})
                
                formset = FSFormSet(request.POST, request.FILES, instance=slice)
                if formset.is_valid():
                    formset.save()
                    slice.committed = True
                    slice.save()
                
            else:
                return HttpResponseServerError(u"Unknown action %s" % action)
            
            return HttpResponseRedirect(reverse('slice_flash_detail'), slice_id)

        except KeyError, e:
            return HttpResponseServerError(u"Missing POST field %s" % e.message)
    else:
        print "<zz>"
        for am in agg_list:
            print "<aa>"
#            am.updateRSpec()
        formset = FSFormSet(instance=slice)
        print "Slice nodeIds: %s" % slice.nodes.values_list('nodeId', flat=True)
        
    return render_to_response("clearinghouse/slice_flash_detail.html",
                              {'slice': slice,
                               'fsformset': formset,
                               })

def slice_get_img(request, slice_id, img_name):
    image_data = open("../../img/%s" % img_name, "rb").read()
    return HttpResponse(image_data, mimetype="image/png")

def slice_get_plugin(request, slice_id):
    jar = open("../../plugin.jar", "rb").read()
    return HttpResponse(jar, mimetype="application/java-archive")

def slice_get_xsd(request, slice_id):
    xsd = open("../plugin.xsd", "rb").read()
    return HttpResponse(xsd, mimetype="application/xml")    

def slice_get_topo(request, slice_id):
    slice = get_object_or_404(Slice, pk=slice_id)
    
    return HttpResponse(
"""<?xml version="1.0" encoding="UTF-8"?>
<document xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<!-- URL to send POST message to on submit button click -->
<submit>
  <url>http://alice.bob/sdkjl</url>
</submit>

<!-- Example of a node in the graph -->
<node>
  <!-- id used to identify the node -->
  <id>12314xlska</id>

  <!-- X and Y coordinates in pixels of node on graph -->
  <x>135</x>
  <y>200</y>

  <!-- images used when selected, unselected, and has error -->
  <sel_img>/img/white_circle.png</sel_img>
  <unsel_img>/img/blue_circle.png</unsel_img>
  <err_img>/img/red_circle.png</err_img>

  <!-- String shown on the graph indicating name of the node -->
  <name>node1</name>

  <!-- Boolean indicating whther to draw 
       node as selected or unselected -->
  <is_selected>False</is_selected>

  <!-- Flag indicating node has an error and should be
       drawn with err_img. -->
  <has_err>False</has_err>
</node>

<node>
  <id>1asd29</id>
  <x>15</x>
  <y>10</y>
  <sel_img>/img/white_circle.png</sel_img>
  <unsel_img>/img/blue_circle.png</unsel_img>
  <err_img>/img/red_circle.png</err_img>
  <name>node2</name>
  <is_selected>True</is_selected>
  <has_err>False</has_err>
</node>

<node>
  <id>xz98ch9o2</id>
  <x>100</x>
  <y>80</y>
  <sel_img>/img/white_circle.png</sel_img>
  <unsel_img>/img/blue_circle.png</unsel_img>
  <err_img>/img/red_circle.png</err_img>
  <name>node3</name>
  <is_selected>False</is_selected>
  <has_err>True</has_err>
</node>

<!-- Example of a description of a link between two nodes -->
<link>
  <id>sdfasaf93</id>
  <!-- Each link must have exactly two endpoints -->
  <src>12314xlska</src>

  <dst>1asd29</dst>

  <!-- Boolean indicating whether or not link is selected -->
  <is_selected>False</is_selected>

  <!-- Boolean indicating whether or not link is selected -->
  <has_err>True</has_err>
</link>

<link>
  <id>xyz</id>
  <src>12314xlska</src>
  <dst>xz98ch9o2</dst>
  <is_selected>True</is_selected>>
  <has_err>False</has_err>
</link>
<link>
  <id>xyz</id>
  <dst>12314xlska</dst>
  <src>xz98ch9o2</src>
  <is_selected>True</is_selected>>
  <has_err>False</has_err>
</link>
</document>
""", mimetype="text/xml"
)
    if request.method == "GET":
        for am in AggregateManager.objects.all():
            am.updateRSpec()
        # get all the local nodes
        nodes = Node.objects.all().exclude(is_remote=True)
        
        # get all the local links
        links = Link.objects.filter(
                    src__ownerNode__is_remote=False,
                    dst__ownerNode__is_remote=False)
                    
        return render_to_response("clearinghouse/flash-xml.xml",
                                  {'nodes': nodes,
                                   'links': links},
                                   mimetype="application/xml")
    else:
        return HttpResponseServerError(u"Unknown method %s to this URL" % request.method)
    
    
    
def am_delete(request, object_id):
    # get the aggregate manager object
    am = get_object_or_404(AggregateManager, pk=object_id)
    am.delete()
    return HttpResponseRedirect(reverse('index'))

def am_create(request):
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

def am_detail(request, am_id):
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

