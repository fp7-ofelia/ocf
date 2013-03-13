from django.core.urlresolvers import reverse
from expedient.clearinghouse.slice.models import Slice
# FIXME: OpenFlow dpeendency
#from openflow.plugin.models import OpenFlowSwitch
import random

def get_node_description(name):
    description = "<strong>Sensor: " + name + "</strong><br/><br/>"
    description += "&#149; <em>Temperature: " + str(random.random()*20)[:5] + "</em><br/><br/>"
    description += "<br clear=left />"
    return description

def get_nodes_links(slice):
    from expedient.common.utils.plugins.resources.node import Node
    # Getting image for the nodes
    try:
        image_url = reverse('img_media_sample_resource', args=("sensor-tiny.png",))
    except:
        image_url = 'sensor-tiny.png'

    sample_resource_nodes = [1, 2, 3, 4]
    nodes = []
    for node in sample_resource_nodes:
         # XXX New: use a class for it
#        nodes.append(Node("sample_resource%s" % str(node), "Sample Resource", get_node_description("sample_resource%s" % str(node), image_url, 101, True, "Barcelona"))
        nodes.append(dict(
            #name = "sample_resource%s" % str(node), value = str(node), group = 3, aggregate = 101, type = "sr_agg",
            name = "sample_resource%s" % str(node), value = str(node), aggregate = 101,
            type = "Sample Resource", description = get_node_description("sample_resource%s" % str(node)),
            image = image_url, available = True, loc = "Barcelona")
        )

    # XXX DANGER!! Hacking the whole topology links, test only
    sample_resource_links = [[0,0],[0,1],[0,2],[0,3],[0,4],[4,5]]
    links = []
    for link in sample_resource_links:
#        try:
#            sId = openflowSwitches[inter.switchID]
#            pId = OpenFlowSwitch.objects.get(id = 125).openflowinterface_set.get(port_num=1).id
#        except:
#            continue
        links.append(
                dict(
                    source = link[0],
                    target = link[1],
                    value = "rsc_id_" + str(link[0]) + "-rsc_id_" + str(link[1])
                ),
        )

#    return [nodes, links, 1]
    return [nodes, [], 1]

def get_ui_data(slice):
    """
    Hook method. Use this very same name so Expedient can get the resources for every plugin.
    """
    ui_context = dict()
    try:
#        ui_context['checked_ids'] = get_checked_ids(slice)
#        ui_context['controller_url'] = get_controller_url(slice)
#        ui_context['allfs'] = FlowSpaceRule.objects.filter(slivers__slice=slice).distinct().order_by('id')
#        ui_context['planetlab_aggs'] = get_planetlab_aggregates(slice)
#        ui_context['openflow_aggs'] = get_openflow_aggregates(slice)
#        ui_context['gfs_list'] = get_gfs(slice)
#        ui_context['ofswitch_class'] = OpenFlowSwitch
#        ui_context['planetlab_node_class'] = PlanetLabNode
#        ui_context['tree_rsc_ids'] = get_tree_ports(ui_context['openflow_aggs'], ui_context['planetlab_aggs'])
        ui_context['nodes'], ui_context['links'], ui_context['n_islands'] = get_nodes_links(slice)
    except Exception as e:
        print "[ERROR] Problem loading UI data for plugin 'sample_resource'. Details: %s" % str(e)
    return ui_context

