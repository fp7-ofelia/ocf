"""
Loads UI data for every plugin and returns a dictionary with all the data.

@date: Feb 20, 2013
@author: CarolinaFernandez
"""

from expedient.clearinghouse.resources.models import Resource
from pluginloader import PluginLoader
from utils import Singleton

class TopologyGenerator():

    # Allows only one instance of this class
    __metaclass__ = Singleton

    # Structure to save groups/islands and their assigned resources
    assigned_groups = []

    @staticmethod
    def check_link_consistency(links, nodes, slice):
        """
        Checks consistency across links.
        Given a link ( A - <link> - B), if any of the endpoints A or B
        do not exist, <link> is removed from the list.
        """
        from django.conf import settings
        consistent_links = []
#        inconsistent_links = []
#        inconsistent_links_message = ""
        nodes_length = len(nodes)
        try:
            for link in links:
                source_node = dict({"id": link['source'], "res_id": None})
                target_node = dict({"id": link['target'], "res_id": None})

                # Convert Resource (Django) IDs into Topology (D3) index IDs
                # (D3 uses integers starting from 0)
                try:
                   # Get back Resource ID from node's array (check first if node.index < #nodes)
                   if source_node['id'] < nodes_length:
                       source_node['res_id'] = nodes[source_node['id']]['value']
                   if target_node['id'] < nodes_length:
                       target_node['res_id'] = nodes[target_node['id']]['value']
                except Exception as e:
                    print "[WARNING] Problem retrieving Resource indices inside TopologyGenerator. Details: %s" % str(e)

                # Check consistency. If both nodes A and B exist, add link to structure
                if str(source_node['res_id']) != "None" and str(target_node['res_id']) != "None":
                    consistent_links.append(link)
                # Otherwise, notify about this missing (and any other) to the Island Manager
                else:
                    # Get data for e-mail
                    try:
                        # Choose the Resource ID which is not None
                        source_id = source_node['res_id'] or source_node['id']
                        source_node_object = Resource.objects.get(id = source_id)
                        source_node['id'] = source_id
                        source_node['name'] = source_node_object.name
                        source_node['agg_id'] = source_node_object.aggregate.pk
                        source_node['agg_name'] = source_node_object.aggregate.name
                    except:
                        source_node['name'] = ""
                        source_node['agg_id'] = ""
                        source_node['agg_name'] = ""
                    try:
                        # Choose the Resource ID which is not None
                        target_id = target_node['res_id'] or target_node['id']
                        target_node_object = Resource.objects.get(id = target_id)
                        target_node['id'] = target_id
                        target_node['name'] = target_node_object.name
                        target_node['agg_id'] = target_node_object.aggregate.pk
                        target_node['agg_name'] = target_node_object.aggregate.name
                    except:
                        target_node['name'] = ""
                        target_node['agg_id'] = ""
                        target_node['agg_name'] = ""

#                    inconsistent_links.append({"source_id": source_node['id'], "source_name": source_node['name'], "source_aggregate_id": source_node['agg_id'], "source_aggregate_name": source_node['agg_name'], "target_id": target_node['id'], "target_name": target_node['name'], "target_aggregate_id": target_node['agg_id'], "target_aggregate_name": target_node['agg_name']})
        except Exception as e:
            print "[WARNING] Problem checking link consistency inside TopologyGenerator. Details: %s" % str(e)

#        # Craft message to send via e-mail
#        if inconsistent_links:
#            for link in inconsistent_links:
#                inconsistent_links_message += "SOURCE\n"
#                inconsistent_links_message += "id: %s\nname: %s\naggregate id: %s\naggregate name: %s\n" % (link['source_id'], link['source_name'], link['source_aggregate_id'], link['source_aggregate_name'])
#                inconsistent_links_message += "TARGET\n"
#                inconsistent_links_message += "id: %s\nname: %s\naggregate id: %s\naggregate name: %s\n\n" % (link['target_id'], link['target_name'], link['target_aggregate_id'], link['target_aggregate_name'])
#
#            from django.contrib.auth.models import User
#            try:
#                user = User.objects.get(settings.ROOT_USERNAME)
#            except:
#                user = User.objects.filter(is_superuser=True)[0]
#            try:
#                from expedient.common.utils.mail import send_mail # Wrapper for django.core.mail__send_mail
#                # Use thread to avoid slow page load when server is unresponsive
#                send_mail(settings.EMAIL_SUBJECT_PREFIX + " Inconsistent links at slice '%s': Expedient" % str(slice.name), "Hi, Island Manager\n\nThis is a warning to notify about some inconsistent links within a topology. This may be happening because a plugin or Aggregate Manager references a node not present in the Aggregate Managers chosen for this slice.\n\nProject: %s\nSlice: %s\nProblematic links:\n\n%s" % (slice.project.name, slice.name, str(inconsistent_links)), from_email = settings.DEFAULT_FROM_EMAIL, recipient_list = [user.email],)
#            except Exception as e:
#                print "[WARNING] Problem sending e-mail to user '%s' (email: %s) with information about link inconsistency inside TopologyGenerator. Details: %s" % (user.username, user.email, str(e))
        return consistent_links

    @staticmethod
    def compute_number_islands(nodes):
        """
        Computes #islands (same to #groups).
        """
        n_islands = 1
        try:
            # Get length of list of unique elements
            n_islands = len(list(set([ n.get("group", 1) for n in nodes ])))
        except Exception as e:
            # Island numbering starts at 0; therefore add 1 to the obtained max value
            n_islands = max([ n.get("group", 1) for n in nodes ])+1 or 1
            print "[WARNING] Number of islands may have not been obtained at TopologyGenerator. Details: %s" % str(e)
        return n_islands

    @staticmethod
    def get_topo_index_from_resource_id(resource_id, nodes):
        """
        Retrieves topology index from the Resource ID.
        """
        d3_index = resource_id
        for index,node in enumerate(nodes):
            if str(resource_id) == str(node['value']):
                # If d3_index = None, return 'None' instead
                d3_index = index
                break
        return d3_index

    @staticmethod
    def get_island_for_nodes(nodes):
        """
        Computes each node island/group through its aggregate manager ID and location.
        """
        from expedient.clearinghouse.aggregate.models import Aggregate
        try:
            for node in nodes:
                am = Aggregate.objects.get(id = node["aggregate"])
                # Group already exists
                try:
                    current_locations = [ group[str(i)] for i,group in enumerate(TopologyGenerator.assigned_groups) ]
                    if am.location in current_locations:
                        node["group"] = int(TopologyGenerator.assigned_groups[current_locations.index(am.location)].keys()[0])
                    else:
                        # New group is added
                        node["group"] = int(TopologyGenerator.assigned_groups[-1].keys()[0])+1
                except Exception as e:
                    if not node.get("group"):
                        node["group"] = 0
                new_entry = {str(node["group"]): am.location}
                # List of sublists: [aggregate, group]
                if new_entry not in TopologyGenerator.assigned_groups:
                    TopologyGenerator.assigned_groups.append(new_entry)
        except Exception as e:
            print "[WARNING] Could not obtain adequate groups for islands in TopologyGenerator. Details: %s" % str(e)
        return nodes

    @staticmethod
    def load_ui_data(slice):
        """
        Calls the method 'get_ui_data' present in each plugin and mix the data for all
        plugins in a dictionary with nodes, links and total number of islands. This data
        will be sent to the topology visor, shown in the slice view.
        """
        plugin_ui_data = dict()
        plugin_ui_data['d3_nodes'] = []
        plugin_ui_data['d3_links'] = []
        plugin_ui_data['n_islands'] = 0
        plugin_ui_data_aux = dict()

        # Iterate over each plugin to get its nodes and links
        for plugin in PluginLoader.plugin_settings:
            try:
                plugin_method = "%s_get_ui_data" % str(plugin)
                plugin_import = PluginLoader.plugin_settings.get(plugin).get("general").get("get_ui_data_location")
                # Check that plugin does have a method to get UI data
                if plugin_import:
                    #exec(plugin_import)
                    tmp = __import__(plugin_import, globals(), locals(), ['get_ui_data'], 0)
                    try:
                        # 1st - get method inside interface ('Plugin'), if present
                        locals()[plugin_method] = getattr(tmp.Plugin, 'get_ui_data')
                    except:
                        # 2nd - get method directly from module
                        locals()[plugin_method] = getattr(tmp, 'get_ui_data')
                    # A dictionary is expected to be returned
                    plugin_ui_data_aux = locals()[plugin_method](slice)

                    # Each Node/Link object's dictionary from the list is retrieved
                    try:
                        [ plugin_ui_data['d3_nodes'].append(node.__dict__) for node in plugin_ui_data_aux.get("nodes", []) ]
                    except:
                        pass
                    try:
                        [ plugin_ui_data['d3_links'].append(link.__dict__) for link in plugin_ui_data_aux.get("links", []) ]
                    except:
                        pass

                plugin_ui_data = dict(plugin_ui_data_aux.items() + plugin_ui_data.items())
            except Exception as e:
                print "[ERROR] Problem loading UI data inside TopologyGenerator. Details: %s" % str(e)

        for link in plugin_ui_data['d3_links']:
            # Convert Resource IDs into Topology index IDs
            try:
               if str(link['source']) != "None" and str(link['target']) != "None":

                   link['source'] = TopologyGenerator.get_topo_index_from_resource_id(link['source'], plugin_ui_data['d3_nodes'])
                   link['target'] = TopologyGenerator.get_topo_index_from_resource_id(link['target'], plugin_ui_data['d3_nodes'])
            except Exception as e:
                print "[WARNING] Problem retrieving Topology indices inside TopologyGenerator. Details: %s" % str(e)

        # Check link consistency
        plugin_ui_data['d3_links'] = TopologyGenerator.check_link_consistency(plugin_ui_data['d3_links'], plugin_ui_data['d3_nodes'], slice)
        plugin_ui_data['d3_nodes'] = TopologyGenerator.get_island_for_nodes(plugin_ui_data['d3_nodes'])
        plugin_ui_data['n_islands'] = TopologyGenerator.compute_number_islands(plugin_ui_data['d3_nodes'])
        return plugin_ui_data

